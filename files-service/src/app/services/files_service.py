import io
from typing import Callable
from uuid import UUID

from types_aiobotocore_s3.client import S3Client

from app.repositories.project_files_repository import ProjectFilesRepository
from app.repositories.user_files_repository import UserFilesRepository
from models import UserFiles, Files, ProjectFiles
from settings import settings


class FilesService:
    def __init__(
            self,
            session_factory: Callable[[], S3Client],
            user_files_repository: UserFilesRepository,
            project_files_repository: ProjectFilesRepository,
    ):
        self._s3_client_factory = session_factory
        self._project_files_repository = project_files_repository
        self._user_files_repository = user_files_repository
        self._bucket_name = settings.aws_settings.s3_service_bucket_name

    async def _upload_file(self, content: bytes, object_key: str, content_type: str, filename: str) -> str:
        async with self._s3_client_factory() as client:
            await client.upload_fileobj(
                Fileobj=io.BytesIO(content),
                Bucket=self._bucket_name,
                Key=object_key,
                ExtraArgs={
                    "ContentType": content_type,
                    "Metadata": {
                        "Original-Filename": filename,
                    },
                },
            )

            return await self.presign_file_url(object_key)

    async def presign_file_url(self, object_key: str) -> str:
        async with self._s3_client_factory() as client:
            return await client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self._bucket_name,
                    "Key": object_key,
                },
                ExpiresIn=3600,
            )

    async def upload_users_avatar(
            self,
            user_id: UUID,
            filename: str,
            size: int,
            content_type: str,
            content: bytes,
    ) -> str:
        object_key = f"users/{user_id}/avatar"

        object_presigned_url = await self._upload_file(
            content,
            object_key,
            content_type,
            filename,
        )

        await self._user_files_repository.create_or_update_file(
            file=Files(
                bucket=self._bucket_name,
                s3_object_key=object_key,
                content_type=content_type,
                original_filename=filename,
                size=size,
            ),
            user_file=UserFiles(
                type='avatar',
                user_id=user_id,
            ),
        )
        return object_presigned_url

    async def upload_projects_photo(
            self,
            project_id: int,
            filename: str,
            size: int,
            content_type: str,
            content: bytes,
    ) -> str:
        object_key = f"projects/{project_id}/photo"

        object_presigned_url = await self._upload_file(
            content,
            object_key,
            content_type,
            filename,
        )

        await self._project_files_repository.create_or_update_file(
            file=Files(
                bucket=self._bucket_name,
                s3_object_key=object_key,
                content_type=content_type,
                original_filename=filename,
                size=size,
            ),
            project_file=ProjectFiles(
                type='avatar',
                project_id=project_id,
            ),
        )
        return object_presigned_url

    async def get_project_photo(self, project_id: int) -> ProjectFiles:
        return await self._project_files_repository.get_file_and_project_file_by_project_id(
            project_id=project_id,
        )

    async def get_user_avatar(self, user_id: UUID) -> UserFiles:
        return await self._user_files_repository.get_file_and_user_file_by_user_id(
            user_id=user_id,
        )
