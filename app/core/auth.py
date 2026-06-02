from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from firebase_admin import auth

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.engine import get_db_session
from app.db.models.user import User
from app.schemas.auth import TokenPayload

security = HTTPBearer()

def verify_firebase_token(credentials: HTTPAuthorizationCredentials=Depends(security)):
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return TokenPayload(**decoded_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = f"Authorization Failed: {str(e)}",headers={"WWW-Authenticate": "Bearer"})

async def get_current_user(token_payload: TokenPayload = Depends(verify_firebase_token),db: AsyncSession = Depends(get_db_session)):
    uid = token_payload.uid
    stmt = select(User).where(User.firebase_uid==uid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    else:
        return user

