from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.db.models.event import MediaTypeEnum
from uuid import UUID
from typing import List
from datetime import date

class EventBase(BaseModel):
    title:str
    description:Optional[str]
    event_date:date
    batch_id:str

class EventMediaBase(BaseModel):
    event_id:UUID
    media_url:str
    media_type: MediaTypeEnum

class EventCreate(EventBase):
    pass

class EventMediaCreate(EventMediaBase):
    pass

class EventResponse(EventBase):
    id:UUID
    media_count:int
    created_at:datetime
    model_config = {"from_attributes": True}

class EventDetailResponse(EventBase):
    media_list:List[EventMediaResponse]
    model_config = {"from_attributes": True}


class EventMediaResponse(EventMediaBase):
    id:UUID
    created_at:datetime
    model_config = {"from_attributes": True}

class EventUpdate(BaseModel):
    title:Optional[str]=None
    description:Optional[str]=None
    event_date:Optional[date]=None
    batch_id:Optional[str]=None

class EventMediaUpdate(BaseModel):
    event_id:Optional[UUID]=None #Only the Event with which the media is associated can be updated
    
