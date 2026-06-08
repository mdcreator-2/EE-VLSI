from fastapi import APIRouter, status, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.resource import ResourceRegister,ResourceIntentRequest, ResourceIntentResponse, ResourceResponse, ResourceUpdate
from app.db.engine import get_db_session
from app.core.auth import get_current_user
from app.repositories.resource_repository import ResourceRepository
from app.core.rbac import require_admin, Role
from app.db.models.user import User, ApprovalStatusEnum
from app.db.models.resource import VaultResource, MaterialTypeEnum
import datetime
from app.services.resource_service import ResourceService


from uuid import UUID

resource_repo = ResourceRepository()
resource_service = ResourceService(resource_repo)

router = APIRouter()

@router.post("/validate-intent",response_model=ResourceIntentResponse)
async def validate_resource_intent(
    payload: ResourceIntentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await resource_service.get_upload_intent(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return result

@router.post("/register",response_model=ResourceResponse)
async def register_resource(
    payload: ResourceRegister,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await resource_service.register_resource(db,payload,current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return result
    


@router.get("/",response_model=List[ResourceResponse])
async def list_resources(db: AsyncSession = Depends(get_db_session), limit: int = 10, offset: int = 0):
    try:
        result= await resource_service.list_resources(db, limit=limit, offset=offset)
        return result 
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.get("/pending", response_model=List[ResourceResponse])
async def list_pending_resources(token_payload=Depends(require_admin),db: AsyncSession = Depends(get_db_session), limit: int = 10, offset: int = 0):
    try:
        result= await resource_service.list_pending_resources(db, limit=limit, offset=offset)
        return result 
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    

