"""Preprocessing and embedding pipeline."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.embeddings.encoder import encode_texts
from app.embeddings.store import VectorStore
from app.models import Embedding, Review, Run
from app.preprocessing.clean import clean_text
from app.preprocessing.dedupe import DedupeIndex, normalized_hash
from app.preprocessing.language import detect_language
from app.preprocessing.spam import is_spam
from app.preprocessing.tokenize import tokenize_stats
from app.preprocessing.translate import translate_review

logger = logging.getLogger(__name__)


def _pending_query(db: Session, version: str, force: bool):
    q = db.query(Review)
    if not force:
        q = q.filter(
            (Review.preprocessing_version.is_(None))
            | (Review.preprocessing_version != version)
        )
    return q.order_by(Review.id)


def build_dedupe_index(db: Session) -> DedupeIndex:
    index = DedupeIndex()
    rows = (
        db.query(Review.id, Review.clean_text, Review.dedupe_hash)
        .filter(Review.is_duplicate.is_(False))
        .filter(Review.clean_text.isnot(None))
        .filter(Review.dedupe_hash.isnot(None))
        .all()
    )
    for rid, clean, dhash in rows:
        if clean and dhash:
            index.seed(rid, clean, dhash)
    return index


def pipeline_status(db: Session, settings: Optional[Settings] = None) -> Dict[str, Any]:
    settings = settings or get_settings()
    version = settings.preprocessing_version
    total = db.query(Review).count()
    pending = _pending_query(db, version, force=False).count()
    embedded = db.query(Embedding).count()
    return {
        "preprocessing_version": version,
        "total_reviews": total,
        "pending": pending,
        "embedded": embedded,
    }


def run_preprocess_pipeline(
    db: Session,
    limit: int = 500,
    force: bool = False,
    settings: Optional[Settings] = None,
    skip_translation: bool = False,
    skip_embeddings: bool = False,
) -> Dict[str, Any]:
    settings = settings or get_settings()
    version = settings.preprocessing_version

    run = Run(phase="preprocess", status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    stats: Dict[str, Any] = {
        "processed": 0,
        "skipped_already_current": 0,
        "spam": 0,
        "duplicate": 0,
        "embedded": 0,
        "translated": 0,
        "errors": 0,
    }

    try:
        pending = _pending_query(db, version, force=force).limit(limit).all()
        if not pending:
            run.status = "completed"
            run.stats_json = stats
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return {"run_id": run.id, "stats": stats}

        dedupe_index = build_dedupe_index(db)
        vector_store = None if skip_embeddings else VectorStore(settings)

        embed_queue: List[Review] = []
        embed_texts: List[str] = []

        for review in pending:
            try:
                clean = clean_text(review.raw_text)
                review.clean_text = clean

                spam_flag, _reason = is_spam(clean)
                review.is_spam = spam_flag

                dhash = normalized_hash(clean)
                is_dup, _canonical, _ = dedupe_index.check(clean, dhash)
                review.is_duplicate = is_dup
                review.dedupe_hash = dhash

                if not is_dup and clean:
                    dedupe_index.register(review.id, clean, dhash)

                lang, conf = detect_language(clean)
                review.language = lang
                review.language_confidence = conf

                analysis_text = clean
                if (
                    not skip_translation
                    and not spam_flag
                    and lang not in ("en", "unknown")
                ):
                    try:
                        translated = translate_review(clean, lang, settings)
                        if translated and translated != clean:
                            review.translated_text = translated
                            analysis_text = translated
                            stats["translated"] += 1
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("translation failed review=%s: %s", review.id, exc)
                        stats["errors"] += 1

                tokens, needs_chunk = tokenize_stats(
                    analysis_text, settings.max_context_tokens
                )
                review.token_count = tokens
                review.needs_chunking = needs_chunk

                if spam_flag:
                    stats["spam"] += 1
                if is_dup:
                    stats["duplicate"] += 1

                review.preprocessing_version = version
                stats["processed"] += 1

                if not spam_flag and not is_dup and analysis_text:
                    embed_queue.append(review)
                    embed_texts.append(analysis_text)

            except Exception as exc:  # noqa: BLE001
                logger.exception("preprocess failed review=%s", review.id)
                stats["errors"] += 1

        db.flush()

        if not skip_embeddings and embed_queue and embed_texts:
            vectors = encode_texts(
                embed_texts, batch_size=settings.preprocess_batch_size
            )
            ids: List[int] = []
            embeddings_list: List[List[float]] = []
            metadatas: List[Dict[str, Any]] = []

            for review, vec in zip(embed_queue, vectors):
                ids.append(review.id)
                embeddings_list.append(vec.tolist())
                metadatas.append(
                    {
                        "review_id": review.id,
                        "source_id": review.source_id,
                        "language": review.language or "unknown",
                    }
                )
                existing = (
                    db.query(Embedding).filter(Embedding.review_id == review.id).first()
                )
                ref = vector_store.vector_ref(review.id)
                if existing:
                    existing.vector_ref = ref
                    existing.model_name = settings.embedding_model
                else:
                    db.add(
                        Embedding(
                            review_id=review.id,
                            vector_ref=ref,
                            model_name=settings.embedding_model,
                        )
                    )

            vector_store.upsert(ids, embeddings_list, metadatas)
            stats["embedded"] = len(ids)

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
