from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    BASE_API_PATH: str
    ORIGINS: list[str]

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    FIRST_ADMIN_EMAIL: str
    FIRST_ADMIN_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM: str
    SECRET_KEY: str

    DEBUG: bool

    FACE_DETECTOR_MODEL: str
    FACE_EMBEDDING_DIMENSION: int
    FACE_EMBEDDING_MODEL: str

    DEEPFACE_API_URL: str
    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()