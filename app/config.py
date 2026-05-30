from pydantic import SecretStr
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env",env_file_encoding="utf-8",extra="ignore")

    PROJECT_NAME: str="EE-VLSI Legacy Platform"
    DEBUG: bool=True
    API_V1_PREFIX: str="/api/v1"
    CORS_ORIGIN: list[str] = ["*"]  # TODO: Add production origins
    
    
if __name__ == '__main__':
    s = Settings()
    print(s)
    

