from pydantic import BaseModel
from datetime import datetime
from app.core.rbac import Role
from app.db.models.user import ApprovalStatusEnum
from typing import Optional, List
from uuid import UUID

class Userbase(BaseModel):
    name:str
    roll_number:str
    batch_id:int
    
class UserCreate(Userbase):
    pass

class UserUpdate(BaseModel):  # Don't inherit from Userbase
    name: Optional[str] = None
    profile_photo_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None

class AdminUserUpdate(Userbase):
    role:Optional[Role] = None
    approval_status:Optional[ApprovalStatusEnum] = None

class UserResponse(Userbase):
    id:UUID
    email:str
    role:Role
    profile_photo_url:Optional[str]
    github_url:Optional[str]
    linkedin_url:Optional[str]
    approval_status:ApprovalStatusEnum
    created_at:datetime
    updated_at:datetime
    model_config = {"from_attributes":True}

class UserListResponse(BaseModel):
    items:List[UserResponse]
    total:int
    page:int
    per_page:int
