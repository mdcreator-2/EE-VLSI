from fastapi import APIRouter,status,Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserCreate,UserResponse
from app.core.auth import verify_firebase_token, get_current_user
from app.db.engine import get_db_session
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPayload
from app.core.rbac import Role
from app.services.user_service import UserService
from app.db.models.user import ApprovalStatusEnum

user_repo = UserRepository()
user_service = UserService(user_repo)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    token_payload: TokenPayload = Depends(verify_firebase_token),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        user = await user_service.register(db,user_in,token_payload.uid,token_payload.email)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user = Depends(get_current_user)):
    return current_user