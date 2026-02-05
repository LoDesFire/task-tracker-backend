from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from starlette import status

from app.services.files_service import FilesService
from helpers.exceptions.repository_exceptions import RepositoryNotFoundException
from helpers.jwt_helper import JWTTokenPayload
from schemas.file_schema import OutFile
from web.dependencies.auth_schema_dependency import JWTBearer
from web.dependencies.service_dependencies import get_files_service

router = APIRouter(prefix="/projects")


@router.post(
    "/{id}",
    response_model=OutFile,
)
async def get_project_file(
        id: int,
        files_service: FilesService = Depends(get_files_service),
        file: UploadFile = File(...),
        _: JWTTokenPayload = Depends(JWTBearer()),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type",
        )
    presigned_url = await files_service.upload_projects_photo(
        id,
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
async def get_project_files(
        id: int,
        files_service: FilesService = Depends(get_files_service),
        _: JWTTokenPayload = Depends(JWTBearer()),
):
    try:
        project_file = await files_service.get_project_photo(project_id=id)
    except RepositoryNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    presigned_url = await files_service.presign_file_url(project_file.file.s3_object_key)
    return OutFile(
        url=presigned_url,
        original_filename=project_file.file.original_filename,
    )
