from pydantic import SecretStr
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8",extra="ignore")

    PROJECT_NAME: str="EE-VLSI Legacy Platform"
    DEBUG: bool=True
    API_V1_PREFIX: str="/api/v1"
    CORS_ORIGIN: list[str] = ["*"]  # TODO: Add production origins
    DATABASE_URL: str="postgresql+asyncpg://user:password@localhost:5432/dbname"
    FIREBASE_SERVICE_ACCOUNT_PATH: str="./firebase-sa.json"
    FIREBASE_PROJECT_ID: str="your-project-id"
    FIREBASE_STORAGE_BUCKET: str="your-project-id.appspot.com"
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    BUCKET_NAME: str
    ALLOWED_EXTENSIONS: list[str] = ["pdf", "png", "jpg", "jpeg"]
    MAX_SIZE_BYTES: int = 200*1024*1024 
    
if __name__ == '__main__':
    s = Settings()
    print(s)
    

