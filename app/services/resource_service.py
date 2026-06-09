from app.repositories.resource_repository import ResourceRepository
from app.db.models.resource import MaterialTypeEnum
from app.db.models.user import ApprovalStatusEnum
from typing import Optional
import boto3
import uuid
from datetime import datetime, timedelta
from app.config import Settings
from app.schemas.resource import ResourceIntentRequest, ResourceIntentResponse, ResourceRegister

settings = Settings()

class ResourceService:
    def __init__(self, resource_repo: ResourceRepository):
        self.resource_repo = resource_repo
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY
        )
    
    async def get_upload_intent(self, request: ResourceIntentRequest) -> ResourceIntentResponse:
        ext = request.file_name.split('.')[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"File extension '{ext}' not allowed")
        
        if request.file_size_bytes > settings.MAX_SIZE_BYTES:
            raise ValueError("File size exceeds the limit")

        file_uid = str(uuid.uuid4())
        upload_path = f"uploads/resources/{file_uid}.{ext}"

        presigned_url = self.s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.BUCKET_NAME,
                "Key": upload_path,
                "ContentType": request.content_type
            },
            ExpiresIn=900
        )

        return ResourceIntentResponse(
            upload_url=presigned_url,
            upload_path=upload_path,
            expires_at=datetime.now() + timedelta(seconds=900)
        )

    async def register_resource(self, session, request: ResourceRegister, user_id: uuid.UUID):
        try:
            self.s3_client.head_object(
                Bucket=settings.BUCKET_NAME,
                Key=request.file_url
            )
        except self.s3_client.exceptions.ClientError:
            raise ValueError("File not found in the upload path")

        result = await self.resource_repo.create(session, request, user_id, ApprovalStatusEnum.PENDING)
        return result
    
    async def list_resources(self, session, batch_id: Optional[int] = None, semester: Optional[int] = None, subject: Optional[str] = None, material_type: Optional[MaterialTypeEnum] = None, page: int = 1, per_page: int = 20):
        offset = (page - 1) * per_page
        resources = await self.resource_repo.get_approved(session, batch_id, semester, subject, material_type, limit=per_page, offset=offset)
        count = await self.resource_repo.count_approved(session, batch_id, semester, subject, material_type)
        return {"items": resources, "total": count, "page": page, "per_page": per_page}

    async def list_pending_resources(self, session, page: int = 1, per_page: int = 20):
        offset = (page - 1) * per_page
        resources = await self.resource_repo.get_pending(session, limit=per_page, offset=offset)
        count = await self.resource_repo.count_pending(session)
        return {"items": resources, "total": count, "page": page, "per_page": per_page}

    async def get_resource(self, session, resource_id: uuid.UUID):
        resource = await self.resource_repo.get_by_id(session, resource_id)
        if not resource:
            raise ValueError("Resource not found")
        return resource

    async def update_status(self, session, resource_id: uuid.UUID, status: ApprovalStatusEnum):
        resource = await self.resource_repo.get_by_id(session, resource_id)
        if not resource:
            raise ValueError("Resource not found")
        result = await self.resource_repo.update_status(session, resource_id, status)
        return result

    async def delete_resource(self, session, user_id: uuid.UUID, resource_id: uuid.UUID):
        resource = await self.resource_repo.get_by_id(session, resource_id)
        if not resource:
            raise ValueError("Resource not found")
        if resource.uploader_id != user_id:
            raise PermissionError("You are not authorized to delete this resource")
        
        # Delete from DB first
        await self.resource_repo.delete(session, resource_id)

        # Then delete from S3 (log failure, don't crash)
        try:
            self.s3_client.delete_object(
                Bucket=settings.BUCKET_NAME,
                Key=resource.file_url
            )
        except Exception as e:
            # Log this - orphan blob in S3 but DB row is already gone
            print(f"WARNING: Failed to delete S3 object {resource.file_url}: {e}")

        return True