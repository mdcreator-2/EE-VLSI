from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.db.models.user import User, ApprovalStatusEnum
from app.core.rbac import Role
from app.schemas.user import UserCreate

class UserRepository:
    async def update_role(self, session: AsyncSession, uid: str, role: Role):
        stmt = update(User).where(User.firebase_uid == uid).values(role=role)
        result = await session.execute(stmt)
        return result.rowcount>0

    async def update_status(self, session: AsyncSession, uid: str, status: ApprovalStatusEnum):
        stmt = update(User).where(User.firebase_uid == uid).values(approval_status=status)
        result = await session.execute(stmt)
        return result.rowcount>0
    
    async def get_pending_students(self, session: AsyncSession) -> List[User]:
        stmt = select(User).where(User.approval_status == ApprovalStatusEnum.PENDING)
        result = await session.execute(stmt)
        return result.scalars().all()