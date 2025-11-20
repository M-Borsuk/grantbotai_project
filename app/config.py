from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str = Field(..., env="MONGO_URI")
    mongo_db_name: str = Field(..., env="MONGO_DB_NAME")
    openrouter_key: str = Field(..., env="OPENROUTER_KEY")
    openrouter_api_base: str = Field(..., env="OPENROUTER_API_BASE")
    openrouter_model: str = Field(..., env="OPENROUTER_MODEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
