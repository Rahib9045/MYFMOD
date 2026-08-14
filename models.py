"""
models.py — Database schema for the AI Recruitment Intelligence System.

Two kinds of account, set at registration and fixed thereafter:
  RECRUITER — posts vacancies, reviews applicants, screens candidates by hand
  SEEKER    — uploads a CV, gets ranked matching vacancies, applies

Tables:
  users        — people who sign in (either role)
  jobs         — vacancies posted by recruiters
  applications — a seeker applying to a job, with the match score at the time
  portfolios   — a recruiter's saved candidate profile
  analyses     — every AI verdict from the manual screening tool

SQLAlchemy 2.0 typed-ORM style (Mapped / mapped_column).
"""

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Account roles
ROLE_RECRUITER = "recruiter"
ROLE_SEEKER = "seeker"
VALID_ROLES = (ROLE_RECRUITER, ROLE_SEEKER)

# Job lifecycle
JOB_OPEN = "open"
JOB_CLOSED = "closed"

# Application lifecycle, in the order a recruiter moves through them
APPLICATION_STATUSES = ("submitted", "reviewed", "shortlisted", "rejected")


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
    # Defaults to recruiter so accounts created before roles existed keep
    # working exactly as they did.
    role: Mapped[str] = mapped_column(String(20), default=ROLE_RECRUITER, nullable=False)

    # Recruiter-only: shown on the vacancies they post.
    company: Mapped[str] = mapped_column(String(200), default="")

    # Seeker-only: their most recently uploaded CV, so matching does not need
    # a re-upload every visit.
    cv_text: Mapped[str] = mapped_column(Text, default="")
    cv_filename: Mapped[str] = mapped_column(String(255), default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    portfolios: Mapped[list["Portfolio"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["Job"]] = relationship(
        back_populates="recruiter", cascade="all, delete-orphan"
    )
    applications: Mapped[list["Application"]] = relationship(
        back_populates="seeker", cascade="all, delete-orphan"
    )

    @property
    def is_recruiter(self) -> bool:
        return self.role == ROLE_RECRUITER

    def to_dict(self) -> dict:
        # NOTE: password_hash is deliberately never serialized.
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "company": self.company,
            "has_cv": bool((self.cv_text or "").strip()),
            "cv_filename": self.cv_filename,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Job(Base):
    """A vacancy posted by a recruiter."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recruiter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[str] = mapped_column(String(200), default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    employment_type: Mapped[str] = mapped_column(String(50), default="Full-time")
    description: Mapped[str] = mapped_column(Text, default="")
    requirements: Mapped[str] = mapped_column(Text, default="")
    skills: Mapped[str] = mapped_column(Text, default="")  # comma-separated
    experience_level: Mapped[str] = mapped_column(String(50), default="")
    salary_range: Mapped[str] = mapped_column(String(100), default="")

    status: Mapped[str] = mapped_column(String(20), default=JOB_OPEN, index=True)

    # Cached SBERT embedding of match_text(), stored as raw float32 bytes.
    # Recomputed whenever the text fields change, so ranking a CV against every
    # open vacancy never re-encodes the job descriptions.
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    recruiter: Mapped["User"] = relationship(back_populates="jobs")
    applications: Mapped[list["Application"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )

    def match_text(self) -> str:
        """The text the matcher embeds. Kept in one place so the cached
        embedding and any live re-encode can never drift apart."""
        return " ".join(
            filter(
                None,
                [
                    self.title,
                    self.description,
                    self.requirements,
                    self.skills,
                    self.experience_level,
                ],
            )
        )

    def to_dict(self, include_counts: bool = False) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "employment_type": self.employment_type,
            "description": self.description,
            "requirements": self.requirements,
            "skills": [s.strip() for s in (self.skills or "").split(",") if s.strip()],
            "experience_level": self.experience_level,
            "salary_range": self.salary_range,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_counts:
            data["applicant_count"] = len(self.applications)
        return data


class Application(Base):
    """A seeker applying to a job. One row per seeker per job."""

    __tablename__ = "applications"
    # A seeker cannot apply to the same vacancy twice.
    __table_args__ = (UniqueConstraint("job_id", "seeker_id", name="uq_application_job_seeker"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    seeker_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Snapshot of the CV as submitted — the seeker may change theirs later, but
    # the recruiter must keep seeing what was actually applied with.
    cv_text: Mapped[str] = mapped_column(Text, default="")
    cover_note: Mapped[str] = mapped_column(Text, default="")
    match_score: Mapped[float] = mapped_column(Float, default=0.0)

    status: Mapped[str] = mapped_column(String(20), default="submitted", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    job: Mapped["Job"] = relationship(back_populates="applications")
    seeker: Mapped["User"] = relationship(back_populates="applications")

    def to_dict(self, include_cv: bool = False, include_job: bool = False) -> dict:
        data = {
            "id": self.id,
            "job_id": self.job_id,
            "status": self.status,
            "match_score": self.match_score,
            "cover_note": self.cover_note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_cv:
            data["cv_text"] = self.cv_text
            data["applicant"] = {
                "id": self.seeker.id,
                "name": self.seeker.name,
                "email": self.seeker.email,
            }
        if include_job and self.job:
            data["job"] = {
                "id": self.job.id,
                "title": self.job.title,
                "company": self.job.company,
                "location": self.job.location,
                "status": self.job.status,
            }
        return data


class Portfolio(Base):
    """A candidate profile a recruiter saved so they can re-run it later."""

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
    # Which path produced this verdict: "groq-<model>" or "local-mlp".
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
