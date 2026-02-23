from fastapi.middleware.cors import CORSMiddleware



from app.core.config import settings

class CustomCORSMiddleware(CORSMiddleware):
    def __init__(self, app):
        super().__init__(
            app=app,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

