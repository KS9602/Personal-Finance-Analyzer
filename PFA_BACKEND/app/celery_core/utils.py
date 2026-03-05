from app.db.connection import AsyncSessionLocal
from app.models.models import CeleryTaskStatus

async def save_task(task_id: int, user_id: int, task_type: str, params=None) -> None:
    async with AsyncSessionLocal() as session:
        entity = CeleryTaskStatus(
            task_id = task_id,
            user_id = user_id,
            task_type = task_type,
            status = "PENDING"
        )
        if params:
            entity.params = params
        session.add(entity)
        await session.commit()
