from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    IDENTITY_SERVICE_URL: str = "http://localhost:8001"
    CATALOGUE_SERVICE_URL: str = "http://localhost:8002"
    HANDSHAKE_SERVICE_URL: str = "http://localhost:8003"
    ORDER_SERVICE_URL: str = "http://localhost:8004"
    DEBUG: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
