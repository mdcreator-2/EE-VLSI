from sqlalchemy import select, update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.db.models.resource import VaultResource, MaterialTypeEnum
from app.db.models.user import ApprovalStatusEnum
from app.core.rbac import Role
from app.schemas.resource import ResourceRegister, ResourceUpdate, ResourceResponse
import uuid.UUID

class ResourceRepository:
    
    async def create(self, session: AsyncSession, resource_in:ResourceRegister, uploader_id: UUID, approval_status: ApprovalStatusEnum) -> VaultResource:
        resource = VaultResource(
            batch_id=resource_in.batch_id,
            semester=resource_in.semester,
            subject=resource_in.subject,
            material_type=resource_in.material_type,
            file_url=resource_in.file_url,
            approval_status=approval_status
        )
        session.add(resource)
        try:
            await session.flush()
        except IntegrityError:
            raise
        return
    
    async def get_pending(self, session:AsyncSession, limit:int, offset:int) -> List[VaultResource]:
        stmt = select(VaultResource).where(VaultResource.approval_status == ApprovalStatusEnum.PENDING).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return result.scalars().all()
        
    async def get_approved(self, session:AsyncSession, limit:int, offset:int) -> List[VaultResource]:
        stmt = select(VaultResource).where(VaultResource.approval_status == ApprovalStatusEnum.APPROVED).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_id(self, session: AsyncSession, id:UUID) -> Optional[VaultResource]:
        stmt = select(VaultResource).where(VaultResource.id == id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    

    async def update_status(self, session:AsyncSession, id:UUID, status:ApprovalStatusEnum) -> bool:
        stmt = update(VaultResource).where(VaultResource.id == id).values(approval_status=status)
        result = await session.execute(stmt)
        return result.rowcount > 0

        
    async def update(self, session: AsyncSession, resource: VaultResource, resource_in: ResourceUpdate) -> VaultResource:
        pass
        # Give me a nice way so that it can automatically update only the changed fields. I do not remember/Know how to do it 
        # I have left this incomplete for now.

    async def delete(self, session: AsyncSession, id: UUID) -> bool:
        stmt = delete(VaultResource).where(VaultResource.id == id)
        result = await session.execute(stmt)
        return result.rowcount > 0