from fastapi import Depends

from app.db.connection import get_db
from app.repositories.users_repository import UsersRepository
from app.services.users_service import UsersService


def get_users_repository(db = Depends(get_db)):
    return UsersRepository(db)

def get_users_service(users_repository: UsersRepository = Depends(get_users_repository)):
    return UsersService(users_repository)