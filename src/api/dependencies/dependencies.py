from typing import Annotated

from fastapi import Depends, Security
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.api.schemas.currency import CurrencyListResponse
from src.api.schemas.user import UserReturnSchema
from src.core.config import db_settings
from src.core.security import TokenTypeEnum, access_token_header
from src.exceptions.services import (
    UserNotFoundException,
    WrongAuthorizationHeaderException,
)
from src.services.auth import AuthService
from src.services.converter import ConverterService
from src.services.user import UserService
from src.utils.unit_of_work import IUnitOfWork, UnitOfWork


async def get_session_maker():
    engine = create_async_engine(db_settings.DATABASE_URL)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return async_session_maker


async def get_unit_of_work(
    async_session_maker=Depends(get_session_maker),
) -> UnitOfWork:
    return UnitOfWork(async_session_maker)


async def get_auth_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AuthService:
    return AuthService(uow)


async def get_user_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> UserService:
    return UserService(uow)


async def get_convert_service() -> ConverterService:
    return ConverterService()


async def validate_access_token(
    header: Annotated[str, Security(access_token_header)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> str:
    if not header:
        raise WrongAuthorizationHeaderException(
            "No Authorization header received"
        )

    bearer, _, token = header.rpartition(" ")
    if bearer.lower() != "bearer":
        raise WrongAuthorizationHeaderException(
            "Check if Bearer is included in Authorization header"
        )

    if not token:
        raise WrongAuthorizationHeaderException(
            "No authorizarion token received"
        )

    decoded_payload = await auth_service.verify_token_and_type(
        token, TokenTypeEnum.ACCESS
    )
    return decoded_payload.sub


async def get_current_user(
    email: Annotated[str, Depends(validate_access_token)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserReturnSchema:
    db_user = await user_service.get_user(email)
    if not db_user:
        raise UserNotFoundException()

    return db_user


async def get_available_currencies(
    current_user: Annotated[UserReturnSchema, Depends(get_current_user)],
    convert_service: Annotated[ConverterService, Depends(get_convert_service)],
) -> CurrencyListResponse:
    currencies = await convert_service.get_available_symbols()
    return CurrencyListResponse(currencies=currencies)
