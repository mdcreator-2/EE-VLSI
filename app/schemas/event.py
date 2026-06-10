from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.db.models.event import MediaTypeEnum
from uuid import UUID
from typing import List
from datetime import date

class EventBase(BaseModel):
    pass

class EventMediaBase(BaseModel):
    pass

class EventCreate(EventBase):
    pass

class EventMediaCreate(EventMediaBase):
    pass

class EventUpdate(EventBase):
    pass

class EventMediaUpdate(EventMediaBase):
    pass

    
