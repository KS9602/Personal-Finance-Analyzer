from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,autoincrement=True, primary_key=True, index=True)
    keycloak_id = Column(String(50), unique=True, index=True, nullable=False)
