from sqlalchemy import select, update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db.models.resource import VaultResource, MaterialTypeEnum
from app.db.models.user import ApprovalStatusEnum
from app.schemas.resource import ResourceRegister, ResourceUpdate
import uuid

class ResourceRepository:
    
    async def create(self, session: AsyncSession, resource_in: ResourceRegister, uploader_id: uuid.UUID, approval_status: ApprovalStatusEnum) -> VaultResource:
        resource = VaultResource(
            batch_id=resource_in.batch_id,
            semester=resource_in.semester,
            subject=resource_in.subject,
            material_type=resource_in.material_type,
            file_url=resource_in.file_url,
            approval_status=approval_status,
            uploader_id=uploader_id
        )
        session.add(resource)
        try:
            await session.flush()
        except IntegrityError:
            raise
        return resource
    
    async def get_approved(self, session: AsyncSession, batch_id: Optional[int], semester: Optional[int], subject: Optional[str], material_type: Optional[MaterialTypeEnum], limit: int = 20, offset: int = 0) -> List[VaultResource]:
        stmt = select(VaultResource).options(selectinload(VaultResource.uploader)).where(VaultResource.approval_status == ApprovalStatusEnum.APPROVED)
        if batch_id:
            stmt = stmt.where(VaultResource.batch_id == batch_id)
        if semester:
            stmt = stmt.where(VaultResource.semester == semester)
        if subject:
            stmt = stmt.where(VaultResource.subject.ilike(f"%{subject}%"))
        if material_type:
            stmt = stmt.where(VaultResource.material_type == material_type)
        stmt = stmt.order_by(VaultResource.created_at.desc()).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def count_approved(self, session: AsyncSession, batch_id: Optional[int] = None, semester: Optional[int] = None, subject: Optional[str] = None, material_type: Optional[MaterialTypeEnum] = None) -> int:
        stmt = select(func.count(VaultResource.id)).where(VaultResource.approval_status == ApprovalStatusEnum.APPROVED)
        if batch_id:
            stmt = stmt.where(VaultResource.batch_id == batch_id)
        if semester:
            stmt = stmt.where(VaultResource.semester == semester)
        if subject:
            stmt = stmt.where(VaultResource.subject.ilike(f"%{subject}%"))
        if material_type:
            stmt = stmt.where(VaultResource.material_type == material_type)
        result = await session.execute(stmt)
        return result.scalar_one()
    
    async def get_pending(self, session: AsyncSession, limit: int = 20, offset: int = 0) -> List[VaultResource]:
        stmt = (
            select(VaultResource)
            .options(selectinload(VaultResource.uploader))
            .where(VaultResource.approval_status == ApprovalStatusEnum.PENDING)
            .order_by(VaultResource.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def count_pending(self, session: AsyncSession) -> int:
        stmt = select(func.count(VaultResource.id)).where(VaultResource.approval_status == ApprovalStatusEnum.PENDING)
        result = await session.execute(stmt)
        return result.scalar_one()

    async def get_by_id(self, session: AsyncSession, id: uuid.UUID) -> Optional[VaultResource]:
        stmt = select(VaultResource).options(selectinload(VaultResource.uploader)).where(VaultResource.id == id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, session: AsyncSession, id: uuid.UUID, status: ApprovalStatusEnum) -> bool:
        stmt = update(VaultResource).where(VaultResource.id == id).values(approval_status=status)
        result = await session.execute(stmt)
        return result.rowcount > 0

    async def update(self, session: AsyncSession, id: uuid.UUID, **kwargs) -> bool:
        stmt = update(VaultResource).where(VaultResource.id == id).values(**kwargs)
        result = await session.execute(stmt)
        return result.rowcount > 0

    async def delete(self, session: AsyncSession, id: uuid.UUID) -> bool:
        stmt = delete(VaultResource).where(VaultResource.id == id)
        result = await session.execute(stmt)
        return result.rowcount > 0