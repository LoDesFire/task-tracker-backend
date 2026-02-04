from fastapi import Depends

from app.repositories import StatisticsRepository
from web.dependencies.motor_dependency import MotorDependency


async def ger_statistics_repository(motor_dependency: MotorDependency = Depends(MotorDependency)):
    return StatisticsRepository(motor_dependency.client)
