from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Generic, TypeVar, Type, List, Optional


Model = TypeVar("Model")

class BaseRepository(Generic[Model]):
    model: Type[Model]

    def __init__(self, session: AsyncSession):
        self.session = session

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


