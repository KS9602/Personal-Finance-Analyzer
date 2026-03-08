from contextlib import contextmanager

from app.db.connection import AsyncSessionLocal, SessionLocal, sync_engine
from app.models.models import CeleryTask, TaskStatus
from enum import Enum
from celery import Task
from sqlalchemy import select


class TaskNames(str, Enum):
    DASHBOARD_RAPORT = "DASHBOARD_RAPORT"


async def save_task(task_id: int, user_id: int, task_type: str, params=None) -> None:
    async with AsyncSessionLocal() as session:
        entity = CeleryTask(
            task_id = task_id,
            user_id = user_id,
            task_type = task_type,
            status = TaskStatus.PENDING
        )
        if params:
            entity.params = params
        session.add(entity)
        await session.commit()




class BaseTask(Task):
    sessionmaker = None
    session = None

    def update_task_status(self,task_id: str, status: str, einfo: str | None = None):
        with self.sessionmaker() as session:
            task = session.execute(
                select(CeleryTask).where(CeleryTask.task_id == task_id)
            ).scalar_one_or_none()
            if task:
                task.status = status
                task.einfo = einfo
                session.commit()

    def __call__(self, *args, **kwargs):

        with self.sessionmaker() as session:
            self.session = session
            try:
                return super().__call__(*args, **kwargs)
            finally:
                self.session = None

    def apply_async(self, args=None, kwargs=None, **options):

        result = super().apply_async(args=args, kwargs=kwargs, **options)

        headers = options.get("headers")
        user_id = headers.get("user_id")
        params = headers.get("params")

        task_name = self.name.split(".")[-1]

        with self.sessionmaker() as session:
            entity = CeleryTask(
                task_id=result.id,
                user_id=user_id,
                task_type=task_name,
                status=TaskStatus.PENDING,
                params=params
            )

            session.add(entity)
            session.commit()

        return result


    def before_start(self, task_id, args, kwargs):
        self.update_task_status(task_id, TaskStatus.PROCESSING)

    def on_success(self, retval, task_id, args, kwargs):
        self.update_task_status(task_id, TaskStatus.DONE)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.update_task_status(task_id, TaskStatus.FAILED, einfo.traceback)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        self.update_task_status(task_id, TaskStatus.RETRY, einfo.traceback)

    @property
    def task_id(self):
        return self.request.id
