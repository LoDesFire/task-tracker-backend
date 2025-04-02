import sqlalchemy
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.repositories.exceptions import (
    RepositoryIntegrityError,
    RepositoryNotFoundException,
)
from src.app.schemas import RegisterUserAppSchema
from src.models import Users


class UserRepository:
    def __init__(self, db_session: async_sessionmaker[AsyncSession]) -> None:
        self.db_session = db_session

    async def get_user_by_email(self, email: str) -> Users:
        """
        Obtaining a user by email
        :param email: user's email address
        :return:
        User database object
        :raises RepositoryNotFoundException
        """
        async with self.db_session() as session:
            stmnt = select(Users).where(Users.email == email)
            scalar_res = await session.scalars(stmnt)
            user = scalar_res.first()

            if user is None:
                raise RepositoryNotFoundException("User not found")

        return user

    async def create_user(self, user_schema: RegisterUserAppSchema) -> Users:
        """
        Creating a new user
        :param user_schema: user's request data
        :return:
        Created user object
        :raises RepositoryIntegrityError
        """
        try:
            async with self.db_session() as session:
                stmnt = insert(Users).values(user_schema.model_dump()).returning(Users)
                scalar_res = await session.scalars(stmnt)
                user = scalar_res.first()
                await session.commit()

        except sqlalchemy.exc.IntegrityError as e:
            raise RepositoryIntegrityError() from e

        return user  # type: ignore
