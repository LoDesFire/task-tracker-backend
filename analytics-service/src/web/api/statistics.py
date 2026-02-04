from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from app.repositories import StatisticsRepository
from helpers.exceptions.repository_exceptions import RepositoryNotFoundException
from helpers.jwt_helper import JWTTokenPayload
from web.schemas import TaskStatusesCounts, UserStatistics, FinishedTasksCount, ProjectTaskAverageDuration
from web.dependencies.auth_schema_dependency import JWTBearer

from web.dependencies.repository_dependencies import ger_statistics_repository

router = APIRouter(prefix="/statistics")


@router.get(
    "/projects/task-statuses",
    response_model=List[TaskStatusesCounts],
)
async def get_task_statuses_counts(
        project_ids: set[int] = Query(),
        token_payload: JWTTokenPayload = Depends(JWTBearer()),
        statistics_repository: StatisticsRepository = Depends(ger_statistics_repository)
):
    user_project_ids = await statistics_repository.user_project_ids(token_payload.sub)
    if not project_ids.issubset(user_project_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return await statistics_repository.task_statuses_count(
        list(project_ids)
    )


@router.get(
    "/project-tasks-counts",
    response_model=UserStatistics,
)
async def get_user_statistics(
        token_payload: JWTTokenPayload = Depends(JWTBearer()),
        statistics_repository: StatisticsRepository = Depends(ger_statistics_repository)
):
    project_statistics = await statistics_repository.user_project_tasks_counts(token_payload.sub)

    return UserStatistics(
        projects_count=len(project_statistics),
        projects=project_statistics,
    )


@router.get(
    "/projects/{project_id}/user/{user_id}",
    response_model=FinishedTasksCount,
)
async def get_finished_in_week_tasks_count(
        project_id: int,
        user_id: UUID,
        token_payload: JWTTokenPayload = Depends(JWTBearer()),
        statistics_repository: StatisticsRepository = Depends(ger_statistics_repository)
):
    user_project_ids = await statistics_repository.user_project_ids(token_payload.sub)
    if project_id not in user_project_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    try:
        statistics = await statistics_repository.finished_in_week_tasks_count(
            user_id,
            project_id,
        )
    except RepositoryNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return statistics


@router.get(
    "/projects/{id}",
    response_model=ProjectTaskAverageDuration,
)
async def get_project_tasks_average_duration(
        id: int,
        token_payload: JWTTokenPayload = Depends(JWTBearer()),
        statistics_repository: StatisticsRepository = Depends(ger_statistics_repository)
):
    user_project_ids = await statistics_repository.user_project_ids(token_payload.sub)
    if id not in user_project_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    try:
        statistics = await statistics_repository.project_tasks_average_duration(id)
    except RepositoryNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


    return statistics
