from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User


class UserRepository:
    model = User

    def __init__(self, session: AsyncSession):
        self.__session = session

    async def add_user(self, user: dict) -> User:
        query = insert(self.model).values(**user).returning(self.model)
        result = await self.__session.execute(query)
        return result.scalar_one()

    async def get_user(self, filters: dict) -> User | None:
        query = select(self.model).filter_by(**filters)
        result = await self.__session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_expression(self, expression) -> User | None:
        query = select(self.model).where(expression)
        result = await self.__session.execute(query)
        return result.first()

    async def update_user(self, filters: dict, values: dict):
        query = (
            update(self.model)
            .filter_by(**filters)
            .values(**values)
            .returning(self.model)
        )
        result = await self.__session.execute(query)
        return result.scalar_one()

    async def delete_user(self, expression) -> bool:
        query = delete(self.model).where(expression)
        result = await self.__session.execute(query)
        return result.rowcount > 0
