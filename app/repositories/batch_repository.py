from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List,Optional
from app.db.models.batch import Batch



class BatchRepository:
    async def create(self, session: AsyncSession, batch_year: int) -> Batch:
        batch = Batch(batch_year=batch_year)
        session.add(batch)
        try:
            await session.flush()
        except IntegrityError:
            raise
        return batch

    async def get_all(self, session: AsyncSession) -> List[Batch]:
        stmt = select(Batch).order_by(Batch.batch_year)
        result = await session.execute(stmt)
        return list(result.scalars().all())

