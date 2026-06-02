from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.db.models.user import User, ApprovalStatusEnum
from app.core.rbac import Role
from app.schemas.user import UserCreate



class AuthRepository:
    async def create(self, session: AsyncSession, user_in:UserCreate, firebase_uid:str, email:str) -> User:
        user=User(
            firebase_uid=firebase_uid,
            name=user_in.name,
            email=email,
            roll_number=user_in.roll_number,
            batch_id=user_in.batch_id,  
            role=Role.STUDENT,
            approval_status=ApprovalStatusEnum.PENDING,
        )
        session.add(user)
        try:
            await session.flush()
        except IntegrityError:
            raise
        return user

    async def get_by_firebase_uid(self,session:AsyncSession, firebase_uid:str) -> Optional[User]:
        stmt = select(User).where(User.firebase_uid == firebase_uid)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
        