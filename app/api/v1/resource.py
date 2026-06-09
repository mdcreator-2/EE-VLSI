from fastapi import APIRouter, status, Depends, HTTPException
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.resource import ResourceRegister, ResourceIntentRequest, ResourceIntentResponse, ResourceResponse, ResourceListResponse
from app.db.engine import get_db_session
from app.core.auth import get_current_user
from app.repositories.resource_repository import ResourceRepository
from app.core.rbac import require_admin
from app.db.models.user import User, ApprovalStatusEnum
from app.db.models.resource import MaterialTypeEnum
from app.services.resource_service import ResourceService

resource_repo = ResourceRepository()
resource_service = ResourceService(resource_repo)

router = APIRouter()

@router.post("/validate-intent", response_model=ResourceIntentResponse)
async def validate_resource_intent(
    payload: ResourceIntentRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await resource_service.get_upload_intent(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return result

@router.post("/register", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def register_resource(
    payload: ResourceRegister,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await resource_service.register_resource(db, payload, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return result

@router.get("/", response_model=ResourceListResponse)
async def list_resources(
    batch_id: Optional[int] = None,
    semester: Optional[int] = None,
    subject: Optional[str] = None,
    material_type: Optional[MaterialTypeEnum] = None,
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db_session)
):
    result = await resource_service.list_resources(db, batch_id, semester, subject, material_type, page, per_page)
    return result

@router.get("/pending", response_model=ResourceListResponse)
async def list_pending_resources(
    token_payload = Depends(require_admin),
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db_session)
):
    result = await resource_service.list_pending_resources(db, page, per_page)
    return result

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await resource_service.get_resource(db, resource_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return result

@router.post("/{resource_id}/approve")
async def approve_resource(
    resource_id: UUID,
    token_payload = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await resource_service.update_status(db, resource_id, ApprovalStatusEnum.APPROVED)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"message": "Resource approved successfully"}

@router.post("/{resource_id}/reject")
async def reject_resource(
    resource_id: UUID,
    token_payload = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await resource_service.update_status(db, resource_id, ApprovalStatusEnum.REJECTED)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"message": "Resource rejected successfully"}

@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await resource_service.delete_resource(db, current_user.id, resource_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return {"message": "Resource deleted successfully"}
