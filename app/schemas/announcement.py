from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.db.models.announcement import AttachmentTypeEnum
from uuid import UUID
from typing import List

class AnnouncementBase(BaseModel):
    title: str
    content: str
    attachment_url: Optional[str] = None
    attachment_type: Optional[AttachmentTypeEnum] = None
    batch_id: Optional[int] = None
    
class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementUpdate(AnnouncementBase):
    pass

class AnnouncementResponse(AnnouncementBase):
    id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class AnnouncementListResponse(BaseModel):
    items: List[AnnouncementResponse]
    total: int
    page: int
    per_page: int
