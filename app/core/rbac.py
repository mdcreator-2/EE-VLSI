from fastapi import HTTPException, Depends, status
from app.core.auth import verify_firebase_token
from enum import IntEnum

class Role(IntEnum):
    STUDENT = 1
    CR = 2
    ADMIN = 3

class RoleChecker:
    def __init__(self, minimum_role: Role):
        self.minimum_role = minimum_role

    def __call__(self, token_payload=Depends(verify_firebase_token)):
        user_level = token_payload.get("role") if isinstance(token_payload, dict) else getattr(token_payload, "role", None)
        if user_level is None:
            user_level = Role.STUDENT.value
            
        if user_level >= self.minimum_role.value:
            return token_payload
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not Authorized')
        
require_student = RoleChecker(Role.STUDENT)
require_cr = RoleChecker(Role.CR)
require_admin = RoleChecker(Role.ADMIN)