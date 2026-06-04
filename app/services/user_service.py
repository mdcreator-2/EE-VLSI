from app.repositories.user_repository import UserRepository
from app.core.rbac import Role
from app.db.models.user import ApprovalStatusEnum
from typing import List, Optional

class UserService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, session, user_in, firebase_uid, email):
        user = await self.user_repo.get_by_firebase_uid(session, firebase_uid)
        if user:
            raise ValueError("User already exists")
        else:
            user = await self.user_repo.create(session, user_in, firebase_uid, email,Role.STUDENT,ApprovalStatusEnum.PENDING)
            return user

    async def get_profile(self, session, user_id):
        user = await self.user_repo.get_by_id(session,user_id)
        if not user:
            raise ValueError("User Not Found")
        else:
            return user

    async def get_profile_by_firebase_uid(self, session, firebase_uid):
        user = await self.user_repo.get_by_firebase_uid(session,firebase_uid)
        if not user:
            raise ValueError("User Not Found")
        else:
            return user

    async def update_profile(self, session, user_id, requester_id, data):
        if user_id != requester_id:
            raise PermissionError("Cannot edit another user's profile")
        else:
            user = await self.user_repo.update(session, user_id,**data.model_dump(exclude_unset=True))
            if not user:
                raise ValueError("User not found")
            else:
                return user

    async def get_directory(self, session, batch_id, page, per_page):
        offset = (page - 1) * per_page
        if batch_id:
            users = await self.user_repo.get_by_batch_id(session,batch_id,limit=per_page,offset=offset)
            count = await self.user_repo.count_by_batch(session,batch_id)
        else:
            users = await self.user_repo.get_all(session,limit=per_page,offset=offset)
            count = await self.user_repo.count_all(session)
        return {"items": users, "total": count, "page": page, "per_page": per_page}

    async def search_users(self, session, query):
        users = await self.user_repo.search_by_name(session, query)
        return users