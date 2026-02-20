from contextlib import asynccontextmanager

from app.core.redis_service import RedisService
from fastapi import FastAPI
import logging

from app.core.logger import setup_logging
from app.core.redis_base import redis_client
from app.db.connection import close_db_engine

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    setup_logging()

    await redis_client.connect()
    app.state.redis = redis_client.get_client()

    yield

    await close_db_engine()
    await redis_client.disconnect()



