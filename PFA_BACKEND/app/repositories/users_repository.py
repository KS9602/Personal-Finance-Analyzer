from sqlalchemy import select

from app.models.user import User

class UsersRepository:
    def __init__(self, db):
        self.db = db

    async def get_by_kc_id(self, sub: str) -> User | None:
        result = await self.db.execute(select(User).where(User.keycloak_id == sub))
        return result.scalar_one_or_none()

    async def create_user(self, sub: str) -> User | None:
        user = User(keycloak_id = sub)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user