from fastapi import APIRouter
from app.api.v1.batch import router as batches_router
from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.users import router as users_router
from app.api.v1.announcements import router as announcements_router
from app.api.v1.resource import router as resources_router
from app.api.v1.event import router as events_router
api_router = APIRouter()

api_router.include_router(batches_router, prefix="", tags=["Batches"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(announcements_router, prefix="/announcements", tags=["Announcements"])
api_router.include_router(resources_router, prefix="/resources", tags=["Resources"])
api_router.include_router(events_router, prefix="/events", tags=["Events"])

@api_router.get("/health")
async def health_check():
    return {"status": "operational", "version": "0.1.0"}
