from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.db.base import Base, TimestampMixin
from typing import Optional
from app.db.models.user import ApprovalStatusEnum
import uuid
import enum

class MaterialTypeEnum(enum.Enum):
    PYQ = "pyq"
    NOTES = "notes"
    LAB = "lab"
    OTHER = "other"

class VaultResource(Base, TimestampMixin):
    __tablename__ = "vault_resources"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,default=uuid.uuid4)
    uploader_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'),nullable=False)
    batch_id: Mapped[int] = mapped_column(ForeignKey('batches.id'),nullable=False)
    semester: Mapped[int] = mapped_column(nullable=False)
    subject: Mapped[str] = mapped_column(nullable=False)
    material_type: Mapped[MaterialTypeEnum] = mapped_column(nullable=False)
    file_url: Mapped[str] = mapped_column(nullable=False)
    approval_status: Mapped[ApprovalStatusEnum] = mapped_column(nullable=False,default=ApprovalStatusEnum.PENDING)

    uploader: Mapped["User"] = relationship("User")
    batch: Mapped["Batch"] = relationship("Batch")