from app.repositories.event_repository import EventRepository
from app.db.models.resource import MaterialTypeEnum
from typing import Optional
import boto3
import uuid
from datetime import datetime, timedelta
from app.config import Settings
from app.schemas.event import EventCreate, EventMediaCreate, EventDetailResponse, EventMediaResponse, EventResponse, EventUpdate, EventMediaUpdate

class event_service:
    def __init__(self, repository:EventRepository):
        self.repository = repository

    