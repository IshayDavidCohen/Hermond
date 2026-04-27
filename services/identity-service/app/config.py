from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "vendor_identity"
    REDIS_URL: str = "redis://localhost:6379"
    CATALOGUE_SERVICE_URL: str = "http://localhost:8002"
    DEBUG: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
