"""UMAP + HDBSCAN clustering and LLM theme labeling."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.embeddings.store import VectorStore
from app.llm.client import LLMRunBudget
from app.llm.groq_client import GroqClient, GroqLLMClient
from app.llm.json_utils import validate_with_repair
from app.llm.prompts import load_prompt_spec, render_prompt
from app.models import Cluster, Embedding, Review, ReviewTheme, Run, Theme
from app.schemas.analysis import THEME_CATEGORIES, ClusterLabelOutput

logger = logging.getLogger(__name__)

PROMPT_FILE = "cluster_label.v1.txt"
REPAIR_FILE = "json_repair.v1.txt"


def _coherence_score(vectors: np.ndarray) -> float:
    if len(vectors) < 2:
        return 1.0
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    unit = vectors / norms
    sim = unit @ unit.T
    n = len(vectors)
    mask = ~np.eye(n, dtype=bool)
    return float(np.clip(sim[mask].mean(), 0.0, 1.0))


def _closest_to_centroid(
    review_ids: List[int],
    vectors: np.ndarray,
    k: int = 10,
) -> List[int]:
    centroid = vectors.mean(axis=0)
    dists = np.linalg.norm(vectors - centroid, axis=1)
    order = np.argsort(dists)
    top = order[: min(k, len(order))]
    return [review_ids[i] for i in top]


def _normalize_category(category: str) -> str:
    for cat in THEME_CATEGORIES:
        if cat.lower() == category.strip().lower():
            return cat
    return "Category Discovery"


async def _label_cluster(
    client: GroqLLMClient,
    sample_texts: List[str],
    model: str,
    prompt_hash: str,
    repair_body: str,
) -> Tuple[Optional[ClusterLabelOutput], Optional[str]]:
    reviews_block = "\n\n".join(f"- {t[:500]}" for t in sample_texts)
    spec = load_prompt_spec(PROMPT_FILE)
    prompt = render_prompt(spec.body, reviews=reviews_block)

    try:
        raw = await client.complete(
            prompt, model=model, max_tokens=400, prompt_hash=prompt_hash
        )
        sync_client = GroqClient(client.settings)

        def repair_fn(raw_payload: str, error: str) -> str:
            repair_prompt = render_prompt(repair_body, error=error, payload=raw_payload[:4000])
            return sync_client.complete(repair_prompt, max_tokens=512)

        parsed, err = validate_with_repair(raw, ClusterLabelOutput, repair_fn=repair_fn)
        return parsed, err
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def _clear_themes(db: Session) -> None:
    db.query(ReviewTheme).delete()
    db.query(Cluster).delete()
    db.query(Theme).delete()


def run_clustering(
    db: Session,
    settings: Optional[Settings] = None,
    force: bool = False,
    min_cluster_size: int = 5,
) -> Dict[str, Any]:
    settings = settings or get_settings()
    run = Run(phase="cluster", status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    stats: Dict[str, Any] = {"clusters": 0, "noise": 0, "themes": 0, "cost_usd": 0.0}

    try:
        import hdbscan
        import umap

        if force:
            _clear_themes(db)
            db.flush()

        rows = (
            db.query(Review.id)
            .join(Embedding, Embedding.review_id == Review.id)
            .filter(Review.is_spam.is_(False))
            .filter(Review.is_duplicate.is_(False))
            .all()
        )
        review_ids = [r[0] for r in rows]
        if len(review_ids) < min_cluster_size:
            run.status = "completed"
            run.stats_json = {**stats, "message": "not enough reviews"}
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return {"run_id": run.id, "stats": run.stats_json}

        store = VectorStore(settings)
        emb_map = store.get_embeddings(review_ids)
        paired = [(rid, emb_map[rid]) for rid in review_ids if rid in emb_map]
        if len(paired) < min_cluster_size:
            run.status = "completed"
            run.stats_json = {**stats, "message": "not enough vectors"}
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return {"run_id": run.id, "stats": run.stats_json}

        ids = [p[0] for p in paired]
        matrix = np.array([p[1] for p in paired], dtype=np.float32)

        reducer = umap.UMAP(
            n_components=5,
            n_neighbors=min(15, len(ids) - 1),
            min_dist=0.1,
            metric="cosine",
            random_state=42,
        )
        reduced = reducer.fit_transform(matrix)

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=3,
            metric="euclidean",
        )
        labels = clusterer.fit_predict(reduced)

        budget = LLMRunBudget(ceiling_usd=settings.llm_run_cost_ceiling_usd)
        spec = load_prompt_spec(PROMPT_FILE)
        repair_spec = load_prompt_spec(REPAIR_FILE)
        model = spec.model or settings.groq_analysis_model
        client = GroqLLMClient(
            settings, budget=budget, max_concurrency=settings.llm_max_concurrency
        )

        unique_labels = sorted(set(labels.tolist()))
        for label in unique_labels:
            if label == -1:
                stats["noise"] = int((labels == -1).sum())
                continue

            member_idx = np.where(labels == label)[0]
            member_ids = [ids[i] for i in member_idx]
            member_vecs = matrix[member_idx]
            coherence = _coherence_score(member_vecs)
            representatives = _closest_to_centroid(
                member_ids, member_vecs, k=min(10, len(member_ids))
            )

            rep_reviews = (
                db.query(Review).filter(Review.id.in_(representatives)).all()
            )
            sample_texts = []
            for r in rep_reviews:
                sample_texts.append(
                    r.translated_text or r.clean_text or r.raw_text
                )

            label_out, err = asyncio.run(
                _label_cluster(
                    client,
                    sample_texts,
                    model,
                    spec.content_hash,
                    repair_spec.body,
                )
            )
            if label_out is None:
                logger.warning("cluster label failed label=%s: %s", label, err)
                continue

            category = _normalize_category(label_out.category)
            theme = Theme(
                label=label_out.label,
                description=label_out.description,
                category=category,
                review_count=len(member_ids),
            )
            db.add(theme)
            db.flush()

            cluster_row = Cluster(
                theme_id=theme.id,
                size=len(member_ids),
                coherence_score=coherence,
                centroid_ref=f"hdbscan:{label}",
            )
            db.add(cluster_row)

            for rid in member_ids:
                existing = (
                    db.query(ReviewTheme)
                    .filter(
                        ReviewTheme.review_id == rid,
                        ReviewTheme.theme_id == theme.id,
                    )
                    .first()
                )
                if not existing:
                    db.add(
                        ReviewTheme(
                            review_id=rid,
                            theme_id=theme.id,
                            confidence=coherence,
                        )
                    )

            stats["clusters"] += 1
            stats["themes"] += 1

        stats["cost_usd"] = round(budget.spent_usd, 4)
        run.cost_estimate = budget.spent_usd
        run.status = "completed"
        run.stats_json = stats
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"run_id": run.id, "stats": stats}

    except Exception as exc:  # noqa: BLE001
        run.status = "failed"
        run.error = str(exc)
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        raise
