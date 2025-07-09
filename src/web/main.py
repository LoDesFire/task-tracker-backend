from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.web.routes import main_router
from web.dependencies.motor_dependency import MotorDependency


@asynccontextmanager
async def lifespan(_: FastAPI):
    MotorDependency.init_connection()
    yield
    MotorDependency.close_connections()


app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
