from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from app.db.models.event import MediaTypeEnum
from uuid import UUID

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: date
    batch_id: Optional[int] = None

# FIX #14: EventMediaCreate does NOT include event_id (comes from URL path)
class EventMediaCreate(BaseModel):
    media_url: str
    media_type: MediaTypeEnum

class EventCreate(EventBase):
    pass

# FIX #12: EventResponse uses media_count computed from ORM's media relationship
class EventResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    event_date: date
    batch_id: Optional[int] = None
    media_count: int
    created_at: datetime
    model_config = {"from_attributes": True}

class EventMediaResponse(BaseModel):
    id: UUID
    event_id: UUID
    media_url: str
    media_type: MediaTypeEnum
    created_at: datetime
    model_config = {"from_attributes": True}

# FIX #13: field name is "media" to match ORM relationship name
class EventDetailResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    event_date: date
    batch_id: Optional[int] = None
    created_at: datetime
    media: List[EventMediaResponse]
    model_config = {"from_attributes": True}

class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    page: int
    per_page: int

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[date] = None
    batch_id: Optional[int] = None

class EventMediaUpdate(BaseModel):
    event_id: Optional[UUID] = None

class MediaIntentRequest(BaseModel):
    event_id: UUID
    file_name: str 
    file_size_bytes: int 
    content_type: str

class MediaIntentResponse(BaseModel):
    upload_url: str      
    upload_path: str     
    expires_at: datetime 
