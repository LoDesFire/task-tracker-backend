from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.models import Users


class UserRepository:
    def __init__(self, db_session: async_sessionmaker[AsyncSession]) -> None:
        self.db_session = db_session

    async def get_user(self, user_id: int) -> Users | None:
        async with self.db_session() as session:
            stmnt = select(Users).where(Users.id == user_id)
            scalar_res = await session.scalars(stmnt)
        return scalar_res.first()
