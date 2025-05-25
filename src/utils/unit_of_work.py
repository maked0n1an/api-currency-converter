from abc import ABC, abstractmethod

from src.db.database import async_session_maker
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
    async def __aexit__(self):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.__session = self.session_factory()

        self.user = UserRepository(self.__session)
        self.jwt_token = JwtTokenRepository(self.__session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()
        await self.__session.close()
        self.__session = None

    async def commit(self):
        await self.__session.commit()

    async def rollback(self):
        await self.__session.rollback()
