from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from starlette import status

from app.services.files_service import FilesService
from helpers.exceptions.repository_exceptions import RepositoryNotFoundException
from helpers.jwt_helper import JWTTokenPayload
from models.base import UsersIDType
from schemas.file_schema import OutFile
from web.dependencies.auth_schema_dependency import JWTBearer
from web.dependencies.service_dependencies import get_files_service

router = APIRouter(prefix="/users")


@router.post(
    "",
    response_model=OutFile,
)
async def create_users_file(
        files_service: FilesService = Depends(get_files_service),
        file: UploadFile = File(...),
        token_payload: JWTTokenPayload = Depends(JWTBearer()),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type",
        )
    presigned_url = await files_service.upload_users_avatar(
        token_payload.sub,
        filename=file.filename,
        size=file.size,
        content_type=file.content_type,
        content=await file.read(),
    )
    return OutFile(
        url=presigned_url,
        original_filename=file.filename,
    )


@router.get(
    "/{id}",
    response_model=OutFile,
)
async def get_user_files(
        id: UsersIDType,
        files_service: FilesService = Depends(get_files_service),
        _: JWTTokenPayload = Depends(JWTBearer()),
):
    try:
        user_file = await files_service.get_user_avatar(user_id=id)
    except RepositoryNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    presigned_url = await files_service.presign_file_url(user_file.file.s3_object_key)
    return OutFile(
        url=presigned_url,
        original_filename=user_file.file.original_filename,
    )
