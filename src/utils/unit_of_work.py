from abc import ABC, abstractmethod

from src.repositories.jwt import JwtTokenRepository
from src.repositories.user import UserRepository


class IUnitOfWork(ABC):
    user: UserRepository
    jwt_token: JwtTokenRepository

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork(IUnitOfWork):
    def __init__(self, async_session_maker):
        self._session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self._session_factory()

        self.user = UserRepository(self.session)
        self.jwt_token = JwtTokenRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()
        await self.session.close()
        self.session = None

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
