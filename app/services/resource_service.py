from app.repositories.resource_repository import ResourceRepository
from app.core.rbac import Role
from app.db.models.resource import MaterialTypeEnum
from app.db.models.user import ApprovalStatusEnum
from typing import List, Optional

class ResourceService:
    def __init__(self, resource_repo: ResourceRepository):
        self.resource_repo = resource_repo
    

 