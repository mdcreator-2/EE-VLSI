from sqlalchemy import select, update, func, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db.models.event import Event, EventMedia, MediaTypeEnum
from app.schemas.event import EventCreate, EventMediaCreate, EventUpdate, EventMediaUpdate
from uuid import UUID

class EventRepository:
    
    async def create_event(self, session: AsyncSession, event_in: EventCreate) -> Event:
        event = Event(
            title=event_in.title,
            description=event_in.description,
            event_date=event_in.event_date,
            batch_id=event_in.batch_id,
        )
        session.add(event)
        try:
            await session.flush()
        except IntegrityError:
            raise
        return event

    async def create_media(self, session: AsyncSession, event_id: UUID, media_in: EventMediaCreate) -> EventMedia:
        media = EventMedia(
            event_id=event_id,
            media_url=media_in.media_url,
            media_type=media_in.media_type
        )
        session.add(media)
        try:
            await session.flush()
        except IntegrityError:
            raise
        return media
    
    # FIX #10: Build WHERE conditionally, include global events (batch_id IS NULL)
    async def get_events(self, session: AsyncSession, batch_id: Optional[int], limit: int = 20, offset: int = 0) -> List[Event]:
        stmt = (
            select(Event)
            .options(selectinload(Event.media))
            .order_by(Event.event_date.desc())
            .limit(limit)
            .offset(offset)
        )
        if batch_id is not None:
            stmt = stmt.where(or_(Event.batch_id == batch_id, Event.batch_id.is_(None)))
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def get_event_by_id(self, session: AsyncSession, event_id: UUID) -> Optional[Event]:
        stmt = select(Event).options(selectinload(Event.media)).where(Event.id == event_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    # FIX #15: Separate count methods for batch vs all
    async def get_events_count(self, session: AsyncSession, batch_id: Optional[int] = None) -> int:
        stmt = select(func.count(Event.id))
        if batch_id is not None:
            stmt = stmt.where(or_(Event.batch_id == batch_id, Event.batch_id.is_(None)))
        result = await session.execute(stmt)
        return result.scalar_one()

    # FIX #6: Repository returns ORM object, not Pydantic schema
    async def get_event_with_media(self, session: AsyncSession, event_id: UUID) -> Optional[Event]:
        stmt = (
            select(Event)
            .options(selectinload(Event.media))
            .where(Event.id == event_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_media_by_id(self, session: AsyncSession, media_id: UUID) -> Optional[EventMedia]:
        stmt = select(EventMedia).where(EventMedia.id == media_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_event(self, session: AsyncSession, event_id: UUID, **kwargs):
        stmt = update(Event).where(Event.id == event_id).values(**kwargs)
        result = await session.execute(stmt)
        return result.rowcount > 0
    
    async def delete_event(self, session: AsyncSession, event_id: UUID) -> bool:
        stmt = delete(Event).where(Event.id == event_id)
        result = await session.execute(stmt)
        return result.rowcount > 0

    async def update_event_media(self, session: AsyncSession, media_id: UUID, **kwargs):
        stmt = update(EventMedia).where(EventMedia.id == media_id).values(**kwargs)
        result = await session.execute(stmt)
        return result.rowcount > 0

    async def delete_event_media(self, session: AsyncSession, media_id: UUID) -> bool:
        stmt = delete(EventMedia).where(EventMedia.id == media_id)
        result = await session.execute(stmt)
        return result.rowcount > 0