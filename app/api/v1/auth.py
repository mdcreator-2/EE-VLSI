from fastapi import APIRouter,status,Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserCreate,UserResponse
from app.core.auth import verify_firebase_token, get_current_user
from app.db.engine import get_db_session
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import TokenPayload

auth_repo= AuthRepository()

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    token_payload: TokenPayload = Depends(verify_firebase_token),
    db: AsyncSession = Depends(get_db_session)
):
    existing_user = await auth_repo.get_by_firestore_id(db, token_payload.uid)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    else:
        try:
            user = await auth_repo.create(db, user_in, token_payload.uid, token_payload.email)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        return user


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user = Depends(get_current_user)):
    return current_user