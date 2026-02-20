
from app.models.models import Users
from app.repositories.users_repository import UsersRepository
import logging

log = logging.getLogger(__name__)

class UsersService:
    def __init__(self,users_repository: UsersRepository):
        self.users_repository = users_repository

    async def get_if_exist_or_create(self, sub: str) -> Users:
        user = await self.users_repository.get_by_kc_id(sub)
        if user: 
            log.info(f"User exist")
            return user
        else:
            log.info(f"User doesnt exist, creating")
            user = Users(keycloak_id=sub)
            return await self.users_repository.add(user)
