from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer
from app.db.base import Base, TimestampMixin
from typing import Optional
import uuid
import enum


class ApprovalStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class User(Base, TimestampMixin):
      __tablename__ = "users"
      id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
      firebase_uid: Mapped[str] = mapped_column(unique=True)
      name: Mapped[str] = mapped_column()
      email: Mapped[str] = mapped_column(unique=True)          # Unique
      roll_number: Mapped[str] = mapped_column(unique=True)     # Unique
      batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"))
      role: Mapped[int] = mapped_column(Integer, default=1)     # 1=STUDENT, 2=CR, 3=ADMIN (uses Role IntEnum from rbac.py)
      profile_photo_url: Mapped[Optional[str]] = mapped_column()
      github_url: Mapped[Optional[str]] = mapped_column()
      linkedin_url: Mapped[Optional[str]] = mapped_column()
      approval_status: Mapped[ApprovalStatusEnum] = mapped_column(default=ApprovalStatusEnum.PENDING)

      # Relationships
      batch: Mapped["Batch"] = relationship("Batch")