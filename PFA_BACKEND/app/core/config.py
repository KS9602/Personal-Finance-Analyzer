from pydantic_settings import BaseSettings
from typing import List

class Setting(BaseSettings):

    KEYCLOAK_URL: str = "http://keycloak:8080"
    REALM: str = "PFA"

    PFA_BACKEND_SECRET: str
    PFA_BACKEND_CLIENT_ID: str = "pfa_backend"
    PFA_BACKEND_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    PFA_BACKEND_LOGOUT_REDIRECT_URI: str = "http://localhost:8000/auth/logout/callback"
    PFA_BACKEND_REGISTER_REDIRECT_URI: str =  "http://localhost:8000/auth/login"
    PFA_BACKEND_CLIENT_SECRET: str

    PFA_FRONTEND_CLIENT_ID: str = "pfa_frontend"
    PFA_FRONTEND_REDIRECT_URI: str = "http://localhost"
    

    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "postgres"
    DB_PORT: str = "5432"
    DB_NAME: str = "pfa_db"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    REDIS_EXPIRE_SEC: int = 3600
    CODE_VERIFIER_EXP: int = 300

    CELERY_BROKER_URL: str

    DASHBOARD_REPORTS_PATH: str = "reports/pdf"

    CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://keycloak:8080",
    ]

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def DB_URL_ASYNC(self) -> str:
        # return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return "postgresql+asyncpg://test:test@postgres_test:5432/db_test"
    @property
    def DB_URL_SYNC(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TOKEN_URL(self) -> str:
        return f"{self.KEYCLOAK_URL}/realms/{self.REALM}/protocol/openid-connect/token"

    def build_logout_url(self,token_id) -> str:
        return (
            f"{self.KEYCLOAK_URL}/realms/{self.REALM}/protocol/openid-connect/logout"
            f"?id_token_hint={token_id}"
            f"&post_logout_redirect_uri={self.PFA_BACKEND_LOGOUT_REDIRECT_URI}"
        )

    @property
    def ISS_URL(self) -> str:
        return f"{self.KEYCLOAK_URL}/realms/{self.REALM}"
    

settings = Setting()