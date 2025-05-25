import secrets
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Header, Response, status

from src.api.dependencies.dependencies import get_auth_service
from src.api.schemas._common import ValidationErrorResponse
from src.api.schemas.auth import AccessToken, AuthTokenPair, UserCredsSchema
from src.exceptions.services import (
    NoCrsfTokenException,
    NoHeaderException,
    NoRefreshTokenException,
)
from src.services.auth import AuthService

router = APIRouter()


@router.post(
    path="/login",
    summary="Login via username and password",
    responses={
        status.HTTP_201_CREATED: {"model": AccessToken},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ValidationErrorResponse
        },
    },
)
async def login(
    creds: UserCredsSchema,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    device_id: str | None = Header(None, alias="X-Device-ID"),
) -> AccessToken:
    if not device_id:
        raise NoHeaderException("Missing required header: X-Device-ID")

    tokens = await auth_service.login(
        username=creds.username,
        password=creds.password,
        device_id=device_id
    )
    csrf_token = secrets.token_urlsafe(32)

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=True,
        secure=False,
        samesite="strict",
    )
    response.headers["X-CSRF-Token"] = csrf_token

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite="strict",
    )

    return AccessToken(access_token=tokens.access_token)


@router.post(
    path="/refresh",
    summary="Refresh tokens",
    responses={
        status.HTTP_201_CREATED: {"model": AuthTokenPair},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    },
)
async def refresh(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    csrf_cookie: str = Cookie(None, alias="csrf_token"),
    refresh_token: str = Cookie(None, alias="refresh_token"),
    csrf_header: str | None = Header(None, alias="X-CSRF-Token"),
    device_id: str | None = Header(None, alias="X-Device-ID"),
) -> AuthTokenPair:
    if not device_id:
        raise NoHeaderException("Missing required header: X-Device-ID")

    if not refresh_token:
        raise NoRefreshTokenException(
            "Invalid request data, please login firstly"
        )

    if not csrf_header:
        raise NoCrsfTokenException("No CSRF-token provided in headers")

    if csrf_header != csrf_cookie:
        raise NoCrsfTokenException("Invalid X-CSRF-Token")

    return await auth_service.refresh_token(refresh_token, device_id)
