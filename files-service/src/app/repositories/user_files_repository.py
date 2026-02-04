from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.repositories.entity_db_repository import EntityDbRepository
from helpers.exceptions.repository_exceptions import RepositoryNotFoundException
from models import UserFiles, Files


class UserFilesRepository(EntityDbRepository[UserFiles]):
    model = UserFiles

    async def get_file_and_user_file_by_user_id(self, user_id: UUID) -> UserFiles:
        async with self.db_session() as session:
            stmt = (
                select(UserFiles)
                .options(joinedload(UserFiles.file))
                .where(UserFiles.user_id == user_id)
            )
            project_file_obj = await session.scalar(stmt)
            if project_file_obj is None:
                raise RepositoryNotFoundException
            return project_file_obj

    async def create_or_update_file(self, file: Files, user_file: UserFiles) -> tuple[Files, UserFiles]:
        async with self.db_session() as session:
            user_file_obj = await self.get_file_and_user_file_by_user_id(user_file.user_id)
            if user_file_obj is None:
                session.add(file)
                user_file.file = file
                session.add(user_file)
            else:
                file.id = user_file_obj.file.id
                user_file.id = user_file_obj.id

            file = await session.merge(file)
            user_file = await session.merge(user_file)

            await session.commit()
            return file, user_file

