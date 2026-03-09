from app.models import Users
from app.repositories.interfaces.IBaseRepository import IBaseRepository
from asyncpg.protocol.protocol import Protocol


class IUsersRepository(IBaseRepository[Users], Protocol):
    async def get_by_kc_id(self, sub: str) -> Users | None: ...
