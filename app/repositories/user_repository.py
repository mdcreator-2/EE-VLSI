from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.db.models.user import User, ApprovalStatusEnum
from app.core.rbac import Role
from app.schemas.user import UserCreate, UserUpdate

class UserRepository:

    async def create(self, session: AsyncSession, user_in:UserCreate, firebase_uid:str, email:str, role: Role, approval_status:ApprovalStatusEnum) -> User:
        user=User(
            firebase_uid=firebase_uid,
            name=user_in.name,
            email=email,
            roll_number=user_in.roll_number,
            batch_id=user_in.batch_id,  
            role=role,
            approval_status=approval_status,
        )
        session.add(user)
        try:
            await session.flush()
        except IntegrityError:
            raise
        return user
        
    async def update(self, session:AsyncSession, user_id:int, **kwargs):
        stmt = update(User).where(User.id == user_id).values(**kwargs)
        result = await session.execute(stmt)
        return result.rowcount>0

    async def update_role(self, session: AsyncSession, uid: str, role: Role):
        stmt = update(User).where(User.firebase_uid == uid).values(role=role)
        result = await session.execute(stmt)
        return result.rowcount>0

    async def update_status(self, session: AsyncSession, uid: str, status: ApprovalStatusEnum):
        stmt = update(User).where(User.firebase_uid == uid).values(approval_status=status)
        result = await session.execute(stmt)
        return result.rowcount>0
    
    async def get_by_firebase_uid(self,session:AsyncSession, firebase_uid:str) -> Optional[User]:
        stmt = select(User).where(User.firebase_uid == firebase_uid)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_by_id(self,session:AsyncSession, user_id:int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_roll_number(self,session:AsyncSession, roll_number:str) -> Optional[User]:
        stmt = select(User).where(User.roll_number == roll_number)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_pending_students(self, session: AsyncSession) -> List[User]:
        stmt = select(User).where(User.approval_status == ApprovalStatusEnum.PENDING)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_batch_id(self,session:AsyncSession, batch_id:int, limit:int=20, offset:int=0) -> List[User]:
        stmt = select(User).where(User.batch_id == batch_id).limit(limit).offset(offset).order_by(User.name)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def count_by_batch(self, session:AsyncSession, batch_id:int) -> int:
        stmt = select(func.count()).select_from(User).where(User.batch_id == batch_id)
        result = await session.execute(stmt)
        return result.scalar_one()

    async def get_all(self,session:AsyncSession, limit:int=20, offset:int=0) -> List[User]:
        stmt = select(User).limit(limit).offset(offset).order_by(User.name)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def count_all(self, session:AsyncSession) -> int:
        stmt = select(func.count()).select_from(User)
        result = await session.execute(stmt)
        return result.scalar_one()
        
    async def search_by_name(self, session:AsyncSession, query:str) -> List[User]:
        stmt = select(User).where(User.name.ilike(f"%{query}%"))
        result = await session.execute(stmt)
        return result.scalars().all()
        