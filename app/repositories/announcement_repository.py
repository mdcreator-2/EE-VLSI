from sqlalchemy import select, update, delete, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db.models.announcement import Announcement, AttachmentTypeEnum
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate
import uuid

class AnnouncementRepository:

    async def create(self, session: AsyncSession, announcement_in: AnnouncementCreate, author_id: uuid.UUID) -> Announcement:
        announcement = Announcement(
            title = announcement_in.title,
            content = announcement_in.content,
            attachment_url = announcement_in.attachment_url,
            attachment_type = announcement_in.attachment_type,
            batch_id = announcement_in.batch_id,
            author_id = author_id
        )
        session.add(announcement)
        try:
            await session.flush()
        except IntegrityError:
            raise
        return announcement
    
    async def get_by_id(self, session: AsyncSession, announcement_id: uuid.UUID) -> Optional[Announcement]:
        stmt = select(Announcement).options(selectinload(Announcement.author)).where(Announcement.id == announcement_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_feed(self, session: AsyncSession, batch_id: int, limit: int = 20, offset: int = 0) -> List[Announcement]:
        stmt = (
            select(Announcement)
            .options(selectinload(Announcement.author))
            .where(or_(Announcement.batch_id == batch_id, Announcement.batch_id.is_(None)))
            .order_by(Announcement.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def count_feed(self, session: AsyncSession, batch_id: int) -> int:
        stmt = select(func.count()).select_from(Announcement).where(or_(Announcement.batch_id == batch_id, Announcement.batch_id.is_(None)))
        result = await session.execute(stmt)
        return result.scalar_one()
    
    async def delete(self, session: AsyncSession, announcement_id: uuid.UUID) -> bool:
        stmt = delete(Announcement).where(Announcement.id == announcement_id)
        result = await session.execute(stmt)
        return result.rowcount > 0

    async def update(self, session: AsyncSession, announcement_id: uuid.UUID, announcement_in: AnnouncementUpdate, author_id: uuid.UUID) -> bool:
        stmt = (
            update(Announcement)
            .where(Announcement.id == announcement_id, Announcement.author_id == author_id)
            .values(**announcement_in.model_dump(exclude_unset=True))
        )
        result = await session.execute(stmt)
        return result.rowcount > 0
