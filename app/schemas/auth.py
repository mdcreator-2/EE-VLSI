from pydantic import BaseModel, EmailStr
from typing import Optional

class TokenPayload(BaseModel):
    model_config = {"extra": "ignore"}
    uid: str
    email: str
    role: Optional[int] = None

