from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.web.routes import main_router
from src.web.schemas import DetailSchema

app = FastAPI()


@app.exception_handler(StarletteHTTPException)
def web_app_exception_handler(_: Request, exc: StarletteHTTPException):
    """
    Exception handler for the FastAPI `HTTPException`. Overrides the default handler.
    """
    detail = DetailSchema.error(exc.detail).model_dump()
    return JSONResponse(detail, status_code=exc.status_code, headers=exc.headers)


app.include_router(main_router)
