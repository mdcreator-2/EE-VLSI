from sqlalchemy import select, update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db.models.event import Event, EventMedia, MediaTypeEnum
from app.db.models.user import ApprovalStatusEnum
from app.schemas.event import EventCreate, EventMediaCreate, EventUpdate, EventMediaUpdate, EventResponse, EventMediaResponse, EventDetailResponse
import uuid

class EventRepository:
    
    async def create_event(self, session:AsyncSession, event_in:EventCreate)->Event:
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

    async def create_media(self, session:AsyncSession, media_in:EventMediaCreate)->EventMedia:
        media = EventMedia(
            event_id=media_in.event_id,
            media_url=media_in.media_url,
            media_type=media_in.media_type
        )
        session.add(media)
        try:
            await session.flush()
        except IntegrityError:
            raise
        return media
    
    async def get_events_by_batch(self,session:AsyncSession, batch_id:int, limit:int=20, offset:int=0)->List[Event]:
        stmt = select(Event).options(selectinload(Event.media)).where(Event.batch_id == batch_id).order_by(Event.event_date.desc()).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def get_event_by_id(self,session:AsyncSession, event_id:uuid.UUID)->Optional[Event]:
        stmt = select(Event).options(selectinload(Event.media)).where(Event.id == event_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_events_count_by_batch(self,session:AsyncSession, batch_id:int)->int:
        stmt = select(func.count(Event.id)).where(Event.batch_id == batch_id)
        result = await session.execute(stmt)
        return result.scalar_one()
    
    async def get_events_count_all(self,session:AsyncSession)->int:
        stmt = select(func.count(Event.id))
        result = await session.execute(stmt)
        return result.scalar_one()

    async def get_event_media_by_event(self, session:AsyncSession, event_id:uuid.UUID)->EventDetailResponse:
        stmt = select(EventMedia).where(EventMedia.event_id == event_id).order_by(EventMedia.created_at.asc())
        result = await session.execute(stmt)
        event_detail_response = EventDetailResponse(
            media_list=result.scalars().all()
        )
        return event_detail_response

    async def update_event(self, session:AsyncSession, event_id: UUID, **kwargs):
        stmt = update(Event).where(Event.id == event_id).values(**kwargs)
        result = await session.execute(stmt)
        return result.rowcount > 0
    
    async def delete_event(self, session:AsyncSession, event_id:UUID)->bool:
        stmt = delete(Event).where(Event.id == event_id)
        result = await session.execute(stmt)
        return result.rowcount > 0

    async def update_event_media(self, session:AsyncSession, media_id:UUID, **kwargs):
        stmt = update(EventMedia).where(EventMedia.id == media_id).values(**kwargs)
        result = await session.execute(stmt)
        return result.rowcount > 0

    async def delete_event_media(self, session:AsyncSession, media_id:UUID)->bool:
        stmt = delete(EventMedia).where(EventMedia.id == media_id)
        result = await session.execute(stmt)
        return result.rowcount > 0