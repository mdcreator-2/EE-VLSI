from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Settings


settings = Settings()

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Application starting up...")
    # Startup
    yield
    # Shutdown
    print("Application shutting down...")


def create_app() ->FastAPI:
    app = FastAPI(title="EE-VLSI Platform API", lifespan=lifespan)

    # add cors

    app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()

@app.get(f"{settings.API_V1_PREFIX}/health")
async def api_v1_health():
    return {"status": "operational", "version": "0.1.0"}

