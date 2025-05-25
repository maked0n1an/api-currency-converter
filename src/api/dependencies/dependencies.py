from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer

from src.api.schemas.user import UserReturnSchema
from src.core.security import (
    JwtAuth,
    JwtPayload,
    TokenTypeEnum,
    access_token_header,
)
from src.exceptions.services import (
    UserNotFoundException,
    WrongAuthorizationHeaderException,
)
from src.services.auth import AuthService
from src.services.user import UserService
from src.utils.unit_of_work import IUnitOfWork, UnitOfWork


async def get_auth_service(
    uow: IUnitOfWork = Depends(UnitOfWork),
) -> AuthService:
    return AuthService(uow)


async def get_user_service(
    uow: IUnitOfWork = Depends(UnitOfWork),
) -> UserService:
    return UserService(uow)


async def parse_jwt_data(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/login")),
) -> JwtPayload:
    payload = JwtAuth.decode_token(token)
    return payload


async def get_access_token_from_header(
    header: Annotated[str, Security(access_token_header)],
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
    return token


async def validate_access_token(
    token: Annotated[str, Depends(get_access_token_from_header)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> str:
    subject_claim = await auth_service.verify_token_and_get_subject_claim(
        token, TokenTypeEnum.ACCESS
    )
    return subject_claim


async def get_current_user(
    email: Annotated[str, Depends(validate_access_token)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserReturnSchema:
    db_user = await user_service.get_user(email)
    if not db_user:
        raise UserNotFoundException()

    return db_user
