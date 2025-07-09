from fastapi import Depends

from app.repositories import UserFilesRepository, ProjectFilesRepository
from app.services.files_service import FilesService
from web.dependencies.db_dependency import DBDependency
from web.dependencies.s3_dependency import S3Dependency


async def get_files_service(
        db: DBDependency = Depends(DBDependency),
        s3_dependency: S3Dependency = Depends(S3Dependency),
):
    return FilesService(
        session_factory=s3_dependency.s3_client_factory,
        user_files_repository=UserFilesRepository(db.db_session),
        project_files_repository=ProjectFilesRepository(db.db_session),
    )
