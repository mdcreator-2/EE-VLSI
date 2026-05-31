from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin
from typing import Optional

class Batch(Base, TimestampMixin):
    __tablename__ = "batches"
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    batch_year: Mapped[int] = mapped_column(unique=True, nullable=False)
    
    # Relationships
    
    