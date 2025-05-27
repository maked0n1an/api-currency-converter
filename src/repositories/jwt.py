from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import JwtToken


class JwtTokenRepository:
    model = JwtToken

    def __init__(self, session: AsyncSession):
        self.__session = session

    async def add_token(self, data: dict) -> None:
        query = insert(self.model).values(**data)
        await self.__session.execute(query)

    async def is_token_revoked(self, token_id: str) -> bool:
        query = select(self.model.is_revoked).filter(self.model.id == token_id)
        result = await self.__session.execute(query)
        return result.scalar() or False

    async def revoke_tokens(self, filters: dict) -> int:
        query = update(self.model).filter_by(**filters).values(is_revoked=True)
        result = await self.__session.execute(query)
        return result.rowcount
