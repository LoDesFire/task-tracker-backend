from typing import List

from pydantic import BaseModel


class TaskCounts(BaseModel):
    amount: int
    percent: float


class TaskStatus(BaseModel):
    status: str
    counts: TaskCounts


class TaskStatusesCounts(BaseModel):
    project_id: int
    total_tasks: int
    task_statuses: list[TaskStatus]


class ProjectStatistics(BaseModel):
    project_id: int
    tasks_count: int
    users_count: int


class UserStatistics(BaseModel):
    projects_count: int
    projects: List[ProjectStatistics]


class FinishedTasksCount(BaseModel):
    project_id: int
    user_id: str
    tasks_count: int


class ProjectTaskAverageDuration(BaseModel):
    project_id: int
    tasks_count: int
    avg_duration_ms: int
    avg_duration_hours: float
