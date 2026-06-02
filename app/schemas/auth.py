from pydantic import BaseModel, EmailStr
from typing import Optional

class TokenPayload(BaseModel):
    uid: str
    email: str

