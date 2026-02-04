from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from settings import settings
from helpers.exceptions.repository_exceptions import RepositoryNotFoundException
from app.repositories.statistics_repository import queries


class StatisticsRepository:
    def __init__(self, motor_client: AsyncIOMotorClient):
        self._mongo_database = motor_client[settings.mongo_settings.db_name]

    async def user_project_ids(self, user_id: UUID):
        return await self._mongo_database.project_users.distinct(
            key="project_id",
            filter={
                "user_id": str(user_id)
            }
        )

    async def task_statuses_count(
            self,
            project_ids: list[int],
    ):
        return await self._mongo_database.tasks.aggregate(
            queries.task_statuses_count_query(project_ids)
        ).to_list(None)

    async def user_project_tasks_counts(
            self,
            user_id: UUID,
    ):
        return await self._mongo_database.project_users.aggregate(
            queries.user_project_tasks_counts_query(
                str(user_id)
            )
        ).to_list(None)

    async def finished_in_week_tasks_count(
            self,
            user_id: UUID,
            project_id: int,
    ):
        result = await self._mongo_database.project_users.aggregate(
            queries.finished_in_week_tasks_count_query(
                project_id,
                str(user_id),
            )
        ).to_list(None)

        if len(result) != 1:
            raise RepositoryNotFoundException
        return result[0]

    async def project_tasks_average_duration(
            self,
            project_id: int,
    ):
        result = await self._mongo_database.tasks.aggregate(
            queries.project_tasks_average_duration_query(project_id)
        ).to_list(None)

        if len(result) != 1:
            raise RepositoryNotFoundException

        return result[0]
