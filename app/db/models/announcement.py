from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import ForeignKey
from app.db.base import Base,TimestampMixin
from typing import Optional
import uuid
import enum

class AttachmentTypeEnum(enum.Enum):
    NONE = "none"
    LINK = "link"
    FILE = "file"
    IMAGE = "image"


class Announcement(Base, TimestampMixin):
    __tablename__ = "announcements"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,default=uuid.uuid4)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)

    attachment_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    attachment_type: Mapped[Optional[AttachmentTypeEnum]] = mapped_column(nullable=False,default=AttachmentTypeEnum.NONE)
    
    batch_id: Mapped[Optional[int]] = mapped_column(ForeignKey('batches.id'), nullable=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), nullable=False)

    # Relationships
    batch: Mapped["Batch"] = relationship("Batch")
    author: Mapped["User"] = relationship("User")