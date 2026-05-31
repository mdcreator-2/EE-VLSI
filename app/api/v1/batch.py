from fastapi import APIRouter,status,Depends
from app.repositories.batch_repository import BatchRepository
from app.schemas.batch import BatchResponse, BatchCreate, BatchUpdate 
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_db_session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

repo = BatchRepository()

router = APIRouter(prefix="/batches", tags=["Batches"])

@router.post("",response_model=BatchResponse,status_code=status.HTTP_201_CREATED)
async def create_batch(
    payload:BatchCreate, 
    session:AsyncSession = Depends(get_db_session)
):
    try:
        batch = await repo.create(session=session, batch_year=payload.batch_year)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Batch already exists")
    return batch
    
@router.get("",response_model=list[BatchResponse])
async def get_batches(session:AsyncSession=Depends(get_db_session)):
    batches = await repo.get_all(session=session)
    return batches