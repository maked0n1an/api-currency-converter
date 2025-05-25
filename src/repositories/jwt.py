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
        return result.scalar()

    async def revoke_tokens(self, email: str, device_id: str):
        conditions = [
            self.model.email == email, 
            self.model.device_id == device_id
        ]

        query = update(self.model).where(*conditions).values(is_revoked=True)
        await self.__session.execute(query)
