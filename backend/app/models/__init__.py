"""SQLAlchemy ORM models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.session import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    config_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    reviews: Mapped[List["Review"]] = relationship(back_populates="source")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_review_source_external"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    clean_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    translated_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_spam: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dedupe_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    raw_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    language_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    preprocessing_version: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    needs_chunking: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    analysis_version: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    analysis_failed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    source: Mapped["Source"] = relationship(back_populates="reviews")
    embedding: Mapped[Optional["Embedding"]] = relationship(back_populates="review")
    analysis: Mapped[Optional["Analysis"]] = relationship(back_populates="review")
    theme_links: Mapped[List["ReviewTheme"]] = relationship(back_populates="review")


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id"), unique=True, nullable=False
    )
    vector_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    review: Mapped["Review"] = relationship(back_populates="embedding")


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    review_links: Mapped[List["ReviewTheme"]] = relationship(back_populates="theme")
    clusters: Mapped[List["Cluster"]] = relationship(back_populates="theme")


class ReviewTheme(Base):
    __tablename__ = "review_themes"
    __table_args__ = (
        UniqueConstraint("review_id", "theme_id", name="uq_review_theme"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), nullable=False)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"), nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    review: Mapped["Review"] = relationship(back_populates="theme_links")
    theme: Mapped["Theme"] = relationship(back_populates="review_links")


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id"), unique=True, nullable=False
    )
    sentiment: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    sentiment_intensity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    emotion: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    complaint_category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    shopping_behaviour: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    discovery_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="success", nullable=False)
    jtbd: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    segment: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    unmet_need: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    motivation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    review: Mapped["Review"] = relationship(back_populates="analysis")


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    theme_id: Mapped[Optional[int]] = mapped_column(ForeignKey("themes.id"), nullable=True)
    centroid_ref: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coherence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    theme: Mapped[Optional["Theme"]] = relationship(back_populates="clusters")


class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    frequency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    example_review_ids: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    customer_segment: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    business_impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    opportunity: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_breakdown: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    rank_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    theme_id: Mapped[Optional[int]] = mapped_column(ForeignKey("themes.id"), nullable=True)
    validation_status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    validations: Mapped[List["Validation"]] = relationship(back_populates="insight")


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    participant_segment: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    jtbd: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pain_points: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    discovery_barriers: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    coding_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    coding_version: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    conducted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Survey(Base):
    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    respondent_segment: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Validation(Base):
    __tablename__ = "validations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    insight_id: Mapped[int] = mapped_column(ForeignKey("insights.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    agreement: Mapped[str] = mapped_column(String(64), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    insight: Mapped["Insight"] = relationship(back_populates="validations")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    insight_id: Mapped[Optional[int]] = mapped_column(ForeignKey("insights.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    reach_score: Mapped[float] = mapped_column(Float, nullable=False)
    severity_score: Mapped[float] = mapped_column(Float, nullable=False)
    north_star_score: Mapped[float] = mapped_column(Float, nullable=False)
    effort_score: Mapped[float] = mapped_column(Float, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    scoring_rationale: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phase: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cost_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    stats_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
