from app.repositories.event_repository import EventRepository
from typing import Optional, List
import boto3
import uuid
from uuid import UUID
from datetime import datetime, timedelta
from app.config import Settings
from app.schemas.event import EventCreate, EventMediaCreate, EventDetailResponse, EventMediaResponse, EventResponse, EventUpdate, EventMediaUpdate, MediaIntentRequest, MediaIntentResponse, EventListResponse

settings = Settings()

class EventService:
    def __init__(self, repository: EventRepository):
        self.repository = repository
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY
        )

    async def create_event(self, session, payload: EventCreate):
        try:
            event = await self.repository.create_event(session, payload)
        except Exception as e:
            raise ValueError(f"Failed to create event: {e}")
        return event

    async def get_upload_intent(self, request: MediaIntentRequest) -> MediaIntentResponse:
        ext = request.file_name.split('.')[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"File extension '{ext}' not allowed")
        
        if request.file_size_bytes > settings.MAX_SIZE_BYTES:
            raise ValueError("File size exceeds the limit")

        file_uid = str(uuid.uuid4())
        upload_path = f"uploads/events/{request.event_id}/{file_uid}.{ext}"

        presigned_url = self.s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.BUCKET_NAME,
                "Key": upload_path,
                "ContentType": request.content_type
            },
            ExpiresIn=900
        )

        return MediaIntentResponse(
            upload_url=presigned_url,
            upload_path=upload_path,
            expires_at=datetime.now() + timedelta(seconds=900)
        )

    # FIX #14: event_id comes as a separate parameter (from URL path)
    async def create_event_media(self, session, event_id: UUID, payload: EventMediaCreate):
        # Verify event exists first
        event = await self.repository.get_event_by_id(session, event_id)
        if not event:
            raise ValueError("Event not found")
        try:
            self.s3_client.head_object(
                Bucket=settings.BUCKET_NAME,
                Key=payload.media_url
            )
        except self.s3_client.exceptions.ClientError:
            raise ValueError("File not found in the upload path")
        event_media = await self.repository.create_media(session, event_id, payload)
        return event_media
    
    # FIX #6: Use get_event_with_media (returns ORM), let FastAPI serialize via response_model
    async def get_event_media(self, session, event_id: UUID):
        event = await self.repository.get_event_with_media(session, event_id)
        if not event:
            raise ValueError("Event not found")
        return event

    async def delete_media(self, session, media_ids: List[UUID]):
        for media_id in media_ids:
            media = await self.repository.get_media_by_id(session, media_id)
            if not media:
                raise ValueError(f"Media {media_id} not found")
            await self.repository.delete_event_media(session, media_id)
            try:
                self.s3_client.delete_object(
                    Bucket=settings.BUCKET_NAME,
                    Key=media.media_url
                )
            except Exception as e:
                print(f"WARNING: Failed to delete S3 object {media.media_url}: {e}")

    # FIX #18: Delete all media S3 objects before deleting the event
    async def delete_event(self, session, event_id: UUID):
        event = await self.repository.get_event_by_id(session, event_id)
        if not event:
            raise ValueError("Event not found")
        # Clean up S3 objects for all media in this event
        for media in event.media:
            try:
                self.s3_client.delete_object(
                    Bucket=settings.BUCKET_NAME,
                    Key=media.media_url
                )
            except Exception as e:
                print(f"WARNING: Failed to delete S3 object {media.media_url}: {e}")
        # CASCADE will delete event_media rows automatically
        await self.repository.delete_event(session, event_id)

    # FIX #11b: unpack EventMediaUpdate with model_dump
    async def update_event(self, session, event_id: UUID, payload: EventUpdate):
        result = await self.repository.update_event(session, event_id, **payload.model_dump(exclude_unset=True))
        if not result:
            raise ValueError("Event not found")
        return result

    async def update_event_media(self, session, media_id: UUID, payload: EventMediaUpdate):
        result = await self.repository.update_event_media(session, media_id, **payload.model_dump(exclude_unset=True))
        if not result:
            raise ValueError("Media not found")
        return result

    async def get_event_by_id(self, session, event_id: UUID):
        event = await self.repository.get_event_by_id(session, event_id)
        if not event:
            raise ValueError("Event not found")
        return event

    # FIX #12: Compute media_count from ORM's media relationship
    # FIX #15: Use unified count that handles None batch_id
    async def get_events(self, session, batch_id: Optional[int], page: int, per_page: int):
        offset = (page - 1) * per_page
        events = await self.repository.get_events(session, batch_id, limit=per_page, offset=offset)
        count = await self.repository.get_events_count(session, batch_id)
        # Build EventResponse with computed media_count
        event_responses = [
            EventResponse(
                id=event.id,
                title=event.title,
                description=event.description,
                event_date=event.event_date,
                batch_id=event.batch_id,
                media_count=len(event.media),
                created_at=event.created_at
            )
            for event in events
        ]
        return EventListResponse(events=event_responses, total=count, page=page, per_page=per_page)
