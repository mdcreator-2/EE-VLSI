from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.db.base import Base, TimestampMixin
from typing import Optional
import uuid
import enum
from datetime import datetime, date

class MediaTypeEnum(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"

class Event(Base):
    __tablename__ = "events"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,default=uuid.uuid4)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    event_date: Mapped[date] = mapped_column(nullable=False)
    batch_id: Mapped[Optional[int]]   = mapped_column(ForeignKey("batches.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    
    # Relationships
    media: Mapped[list["EventMedia"]] = relationship(back_populates="event", cascade="all, delete-orphan")

class EventMedia(Base):
    __tablename__ = "event_medias"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    media_url: Mapped[str] = mapped_column(nullable=False)
    media_type: Mapped[MediaTypeEnum] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    
    # Relationships
    event: Mapped["Event"] = relationship(back_populates="media")