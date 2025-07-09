from fastapi import FastAPI
from src.web.routes import main_router

app = FastAPI()

app.include_router(main_router)
