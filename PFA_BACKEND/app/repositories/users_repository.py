from sqlalchemy import select

from app.models.models import Users
from app.repositories.base_repository import BaseRepository

class UsersRepository(BaseRepository[Users]):
    model = Users

    async def get_by_kc_id(self, sub: str) -> Users | None:
        result = await self.session.execute(select(Users).where(Users.keycloak_id == sub))
        return result.scalar_one_or_none()
