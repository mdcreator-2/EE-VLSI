from fastapi import APIRouter, status, Depends, HTTPException
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.announcement import AnnouncementCreate, AnnouncementResponse, AnnouncementUpdate, AnnouncementListResponse
from app.db.engine import get_db_session
from app.core.auth import get_current_user
from app.repositories.announcement_repository import AnnouncementRepository
from app.core.rbac import require_cr, require_admin
from app.services.announcement_service import AnnouncementService
from app.db.models.user import User

router = APIRouter()
announcement_repo = AnnouncementRepository()
announcement_service = AnnouncementService(announcement_repo)

@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement_in: AnnouncementCreate,
    token = Depends(require_cr),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        announcement = await announcement_service.create_announcement(db, announcement_in, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return announcement

@router.get("/", response_model=AnnouncementListResponse)
async def get_announcements(
    batch_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db_session)
):
    result = await announcement_service.get_announcements(db, batch_id, page, per_page)
    return result

@router.get("/{id}", response_model=AnnouncementResponse)
async def get_announcement(id: UUID, db: AsyncSession = Depends(get_db_session)):
    try:
        announcement = await announcement_service.get_announcement(db, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return announcement

@router.put("/{id}")
async def update_announcement(
    id: UUID,
    announcement_in: AnnouncementUpdate,
    token = Depends(require_cr),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await announcement_service.update_announcement(db, id, announcement_in, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"message": "Announcement updated successfully"}

@router.delete("/{id}")
async def delete_announcement(
    id: UUID,
    token = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await announcement_service.delete_announcement(db, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"message": "Announcement deleted successfully"}