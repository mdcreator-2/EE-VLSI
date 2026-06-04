from app.repositories.announcement_repository import AnnouncementRepository
from app.core.rbac import Role
from app.db.models.announcement import Announcement
from typing import List, Optional
import uuid

class AnnouncementService:

    def __init__(self, announcement_repo: AnnouncementRepository):
        self.announcement_repo = announcement_repo

    async def create_announcement(self, session, announcement_in, author_id: uuid.UUID):
        announcement = await self.announcement_repo.create(session, announcement_in, author_id)
        return announcement

    async def get_announcements(self, session, batch_id, page, per_page):
        offset = (page - 1) * per_page
        announcements = await self.announcement_repo.get_feed(session, batch_id, limit=per_page, offset=offset)
        count = await self.announcement_repo.count_feed(session, batch_id)
        return {"items": announcements, "total": count, "page": page, "per_page": per_page}

    async def get_announcement(self, session, id):
        announcement = await self.announcement_repo.get_by_id(session, id)
        if not announcement:
            raise ValueError("Announcement not found")
        return announcement

    async def update_announcement(self, session, id, announcement_in, author_id: uuid.UUID):
        result = await self.announcement_repo.update(session, id, announcement_in, author_id)
        if not result:
            raise ValueError("Announcement not found or you are not the author")
        return result

    async def delete_announcement(self, session, id):
        result = await self.announcement_repo.delete(session, id)
        if not result:
            raise ValueError("Announcement not found")
        return result