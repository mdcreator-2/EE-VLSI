from fastapi import APIRouter, status, Depends, HTTPException
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.event import EventCreate, EventMediaCreate, MediaIntentRequest, MediaIntentResponse, EventResponse, EventListResponse, EventMediaResponse, EventDetailResponse
from app.db.engine import get_db_session
from app.core.auth import get_current_user
from app.repositories.event_repository import EventRepository
from app.core.rbac import require_admin, require_cr
from app.db.models.user import User
from app.services.event_service import EventService

event_repo = EventRepository()
event_service = EventService(event_repo)

router = APIRouter()

@router.post("/validate-intent", response_model=MediaIntentResponse)
async def validate_media_intent(
    payload: MediaIntentRequest,
    current_user: User = Depends(get_current_user)):
    try:
        result = await event_service.get_upload_intent(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return result

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    token_payload = Depends(require_cr),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)):
    try:
        result = await event_service.create_event(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return result

# FIX #14: event_id comes from URL path, not request body
@router.post("/{event_id}/media", response_model=EventMediaResponse, status_code=status.HTTP_201_CREATED)
async def create_media(
    event_id: UUID,
    payload: EventMediaCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)):
    try:
        result = await event_service.create_event_media(db, event_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return result

@router.get("/", response_model=EventListResponse)
async def list_events(
    batch_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db_session)):
    result = await event_service.get_events(db, batch_id, page, per_page)
    return result

@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event_with_media(event_id: UUID, db: AsyncSession = Depends(get_db_session)):
    try:
        result = await event_service.get_event_media(db, event_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return result

@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID,
    token_payload = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)):
    try:
        await event_service.delete_event(db, event_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"message": "Event deleted successfully"}

# FIX #4b: token_payload uses = not :
@router.delete("/{event_id}/media")
async def delete_media(
    event_id: UUID,
    media_ids: List[UUID],
    token_payload = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)):
    try:
        await event_service.delete_media(db, media_ids)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"message": "Media deleted successfully"}