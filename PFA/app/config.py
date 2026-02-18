from pydantic_settings import BaseSettings


class Setting(BaseSettings):
    KEYCLOAK_URL: str = "http://localhost:9000"
    REALM: str = "PFA"
    CLIENT_ID: str = "PFA_FRONTEND"
    REDIRECT_URI: str = "http://localhost:3000"

    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "postgres"
    DB_PORT: str = "5432"
    DB_NAME: str = "pfa_db"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    REDIS_EXPIRE_SEC: int = 3600

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Setting()