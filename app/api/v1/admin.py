from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserResponse
from app.db.engine import get_db_session
from app.repositories.user_repository import UserRepository
from app.core.rbac import require_admin, Role
from app.core.claims import set_user_role
from app.db.models.user import ApprovalStatusEnum


user_repo = UserRepository()

router = APIRouter()

@router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users(token = Depends(require_admin), db: AsyncSession = Depends(get_db_session)):
    users = await user_repo.get_pending_students(db)
    return users

@router.post("/users/{uid}/role")
async def update_user_role(uid: str, role: Role, token = Depends(require_admin), db: AsyncSession = Depends(get_db_session)):
    result = await user_repo.update_role(db, uid, role)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    set_user_role(uid, role)
    return {"message": "User role updated successfully"}

@router.post("/users/{uid}/approve")
async def approve_user(uid: str, token = Depends(require_admin), db: AsyncSession = Depends(get_db_session)):
    result = await user_repo.update_status(db, uid, ApprovalStatusEnum.APPROVED)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User approved successfully"}