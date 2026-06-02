from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.db.base import Base, TimestampMixin
from typing import Optional
import uuid
from uuid import uuid4
from sqlalchemy import Enum
import enum

class RoleEnum(enum.Enum):
    STUDENT = "student"
    CR = "cr"
    ADMIN = "admin"

class ApprovalStatusEnum(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base,TimestampMixin):
      __tablename__ = "users"
      id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
      firebase_uid: Mapped[str] = mapped_column(unique=True)
      name: Mapped[str] = mapped_column()
      email: Mapped[str] = mapped_column(unique=True)          # Unique
      roll_number: Mapped[str] = mapped_column(unique=True)     # Unique
      batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"))
      role: Mapped[RoleEnum]  = mapped_column(Enum(RoleEnum))       # PostgreSQL ENUM
      profile_photo_url: Mapped[Optional[str]] = mapped_column()
      github_url: Mapped[Optional[str]] = mapped_column()
      linkedin_url: Mapped[Optional[str]] = mapped_column()
      approval_status: Mapped[ApprovalStatusEnum] = mapped_column(Enum(ApprovalStatusEnum),default=ApprovalStatusEnum.PENDING)

      # Relationships
      batch: Mapped["Batch"] = relationship("Batch") #Need to go through Foriegn Key and Relationships again. 