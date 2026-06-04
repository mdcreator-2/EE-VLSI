from fastapi import APIRouter, status, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserResponse,UserListResponse, UserUpdate
from app.db.engine import get_db_session
from app.core.auth import get_current_user
from app.repositories.user_repository import UserRepository
from app.core.rbac import require_admin, Role
from app.core.claims import set_user_role
from app.db.models.user import User, ApprovalStatusEnum
from app.services.user_service import UserService
from uuid import UUID
user_repo = UserRepository()
user_service = UserService(user_repo)

router = APIRouter()

@router.get("/directory",response_model=UserListResponse)
async def get_user_directory(batch_id: Optional[int]=None, page: int = 1, per_page: int = 20, db: AsyncSession = Depends(get_db_session)):
    try:
        result = await user_service.get_directory(db,batch_id,page,per_page)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return UserListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"]
    )
    
@router.get("/directory/search",response_model=List[UserResponse])
async def search_users(q:str, db: AsyncSession = Depends(get_db_session)):
    try:
        result = await user_service.search_users(db, q)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return result
    

@router.get("/{user_id}",response_model=UserResponse)
async def get_user_by_id(user_id:UUID,db: AsyncSession = Depends(get_db_session)):
    try:
        user = await user_service.get_profile(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return user

@router.patch("/{user_id}")
async def update_user(user_id:UUID, data:UserUpdate,db: AsyncSession = Depends(get_db_session),current_user:User=Depends(get_current_user)): 
    try:
        result = await user_service.update_profile(db, user_id, current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {"message":"User updated successfully"}

