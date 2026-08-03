"""
models.py — Database schema for the AI Recruitment Intelligence System.

Three tables:
  users      — people who sign in
  portfolios — a saved candidate profile (resume + interview transcript)
  analyses   — every AI verdict ever produced, tied to the user who ran it

SQLAlchemy 2.0 typed-ORM style (Mapped / mapped_column).
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    """Timezone-aware UTC timestamp (datetime.utcnow() is deprecated in 3.12)."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    portfolios: Mapped[list["Portfolio"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        # NOTE: password_hash is deliberately never serialized.
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Portfolio(Base):
    """A candidate profile the user saved so they can re-run it later."""

    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    resume: Mapped[str] = mapped_column(Text, default="")
    transcript: Mapped[str] = mapped_column(Text, default="")
    job_description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="portfolios")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="portfolio")

    def to_dict(self, include_text: bool = True) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_text:
            data.update(
                {
                    "resume": self.resume,
                    "transcript": self.transcript,
                    "job_description": self.job_description,
                }
            )
        return data


class Analysis(Base):
    """One saved AI verdict — the 'answer' for a candidate/job pairing."""

    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    portfolio_id: Mapped[int | None] = mapped_column(
        ForeignKey("portfolios.id", ondelete="SET NULL"), nullable=True
    )

    resume: Mapped[str] = mapped_column(Text, default="")
    transcript: Mapped[str] = mapped_column(Text, default="")
    job_description: Mapped[str] = mapped_column(Text, default="")

    probability: Mapped[float] = mapped_column(Float, nullable=False)
    decision: Mapped[str] = mapped_column(String(16), nullable=False)
    advice: Mapped[str] = mapped_column(Text, default="")
    # Which path produced this verdict: "groq-llama-3.3-70b" or "local-mlp".
    engine: Mapped[str] = mapped_column(String(64), default="unknown")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="analyses")
    portfolio: Mapped["Portfolio | None"] = relationship(back_populates="analyses")

    def to_dict(self, include_inputs: bool = False) -> dict:
        data = {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "probability": self.probability,
            "decision": self.decision,
            "advice": self.advice,
            "engine": self.engine,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_inputs:
            data.update(
                {
                    "resume": self.resume,
                    "transcript": self.transcript,
                    "job_description": self.job_description,
                }
            )
        else:
            # Enough to recognize the row in a history list without shipping full text.
            data["job_preview"] = (self.job_description or "")[:140]
        return data
