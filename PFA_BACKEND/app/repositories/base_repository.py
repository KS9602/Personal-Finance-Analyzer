from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, Select
from typing import Generic, TypeVar, Type, List, Optional, Any

Model = TypeVar("Model")

class BaseRepository(Generic[Model]):
    model: Type[Model]

    def __init__(self, session: AsyncSession):
        self.session = session


    async def exe_aync(self, stmt: Select[Any]):
        return await self.session.execute(stmt)

    def exe_sync(self, stmt: Select[Any]):
        return self.session.execute(stmt)

    async def get_all_by_user(self, user_id: str) -> List[Model]:
        stmt = (select(self.model).where(self.model.user_id == user_id))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_by_user_page(self,user_id: int, page: int, size: int) -> List[Model]:
        stmt = (select(self.model)
                .where(self.model.user_id == user_id)
                .order_by(self.model.id.desc())
                .offset((page -1) * size)
                .limit(size)

        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_count_by_user(self, user_id: int) -> int:
        stmt = (select(func.count())
                .where(self.model.user_id == user_id)
                )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_count(self) -> int:
        stmt = (select(func.count()).select_from(self.model))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_id(self, entity_id: int) -> Optional[Model]:
        return await self.session.get(self.model, entity_id)

    async def get_all(self) -> List[Model]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def exists(self, entity_id: int) -> bool:
        return await self.get_by_id(entity_id) is not None

    async def add(self, entity: Model) -> Model:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def add_many(self, entities: List[Model]) -> List[Model]:
        self.session.add_all(entities)
        await self.session.commit()
        return entities

    async def update(self, entity: Model) -> Model:
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update_by_id(self, entity_id: int, values: dict) -> None:
        await self.session.execute(
            update(self.model)
            .where(self.model.id == entity_id)
            .values(**values)
        )
        await self.session.commit()

    async def delete(self, entity: Model) -> None:
        await self.session.delete(entity)
        await self.session.commit()

    async def delete_by_id(self, entity_id: int) -> None:
        await self.session.execute(
            delete(self.model)
            .where(self.model.id == entity_id)
        )
        await self.session.commit()


