from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.repositories.entity_db_repository import EntityDbRepository
from helpers.exceptions.repository_exceptions import RepositoryNotFoundException
from models import ProjectFiles, Files


class ProjectFilesRepository(EntityDbRepository[ProjectFiles]):
    model = ProjectFiles

    async def get_file_and_project_file_by_project_id(self, project_id: int) -> ProjectFiles:
        async with self.db_session() as session:
            stmt = (
                select(ProjectFiles)
                .options(joinedload(ProjectFiles.file))
                .where(ProjectFiles.project_id == project_id)
            )
            project_file_obj = await session.scalar(stmt)
            if project_file_obj is None:
                raise RepositoryNotFoundException
            return project_file_obj



    async def create_or_update_file(self, file: Files, project_file: ProjectFiles) -> tuple[Files, ProjectFiles]:
        async with self.db_session() as session:
            try:
                project_file_obj = await self.get_file_and_project_file_by_project_id(
                    project_file.project_id,
                )
                file.id = project_file_obj.file.id
                project_file.id = project_file_obj.id
            except RepositoryNotFoundException:
                session.add(file)
                project_file.file = file
                session.add(project_file)

            file = await session.merge(file)
            project_file = await session.merge(project_file)

            await session.commit()
            return file, project_file
