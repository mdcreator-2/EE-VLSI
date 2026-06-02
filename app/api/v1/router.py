from fastapi import APIRouter
from app.api.v1.batch import router as batches_router
from app.api.v1.auth import router as auth_router
api_router = APIRouter()

api_router.include_router(batches_router, prefix="", tags=["Batches"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@api_router.get("/health")
async def health_check():
    return {"status": "operational", "version": "0.1.0"}
