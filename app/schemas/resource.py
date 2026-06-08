from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.db.models.resource import MaterialTypeEnum
from app.db.models.user import ApprovalStatusEnum
from uuid import UUID
from typing import List

class ResourceBase(BaseModel):
    batch_id: int
    semester: int
    subject: str
    material_type: MaterialTypeEnum
    file_url: str

class ResourceRegister(ResourceBase):
    pass

class ResourceResponse(ResourceBase):
    id: UUID
    uploader_id: UUID
    approval_status: ApprovalStatusEnum
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class ResourceUpdate(BaseModel):
    batch_id: Optional[int] = None
    semester: Optional[int] = None
    subject: Optional[str] = None
    material_type: Optional[MaterialTypeEnum] = None
    file_url: Optional[str] = None
    approval_status: Optional[ApprovalStatusEnum] = None
    model_config = {"from_attributes": True}

class ResourceListResponse(BaseModel):
    items: List[ResourceResponse]
    total: int
    page: int
    per_page: int

class ResourceIntentRequest(BaseModel):
    file_name: str 
    file_size_bytes: int 
    content_type: str  

class ResourceIntentResponse(BaseModel):
    upload_url: str      
    upload_path: str     
    expires_at: datetime 

