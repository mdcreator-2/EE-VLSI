from app.repositories.resource_repository import ResourceRepository
from app.core.rbac import Role
from app.db.models.resource import MaterialTypeEnum
from app.db.models.user import ApprovalStatusEnum
from typing import List, Optional
import boto3
import uuid
from datetime import datetime, timedelta
from app.config import Settings
from app.schemas.resource import ResourceIntentRequest, ResourceIntentResponse,ResourceRegister,ResourceResponse
from app.db.models.resource import VaultResource,MaterialTypeEnum
from app.db.models.user import ApprovalStatusEnum

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
    
    async def get_upload_intent(self,request:ResourceIntentRequest) -> ResourceIntentResponse:
        ext = request.file_name.split('.')[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"File extension {ext} not allowed")
        
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
            expires_at=datetime.now() + timedelta(seconds=300)
        )

    
    async def register_resource(self,session,request:ResourceRegister,user_id:UUID) -> VaultResource:
        try:
            self.s3_client.head_object(
                Bucket=settings.BUCKET_NAME,
                Key=request.upload_path
            )
        except self.s3_client.exceptions.ClientError as e:
            raise ValueError("File not found in the upload path")

        result = await self.resource_repo.create(session,request,user_id, ApprovalStatusEnum.PENDING)
        return result
    
    async def delete_resource(self,session,user_id:UUID,resource_id:UUID) -> bool:
        resource = await self.resource_repo.get_by_id(session,resource_id)
        if not resource:
            raise ValueError("Resource not found")
        if resource.uploader_id != user_id:
            raise ValueError("You are not authorized to delete this resource")
        
        result = await self.resource_repo.delete(session,resource_id)

        return result

    async def list_resources(self,db,limit:int=10,offset:int=0):
        try:
            result = await self.resource_repo.get_approved(db, limit, offset)
        except Exception as e:
            raise ValueError(str(e))
        return result

        

        