import secrets
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Header, Response, status

from src.api.dependencies.dependencies import (
    get_auth_service,
    get_current_user,
)
from src.api.schemas._common import ValidationErrorResponse
from src.api.schemas.auth import AccessToken, LogoutResponse, UserCredsSchema
from src.api.schemas.user import UserReturnSchema
from src.exceptions.services import (
    NoCsrfTokenException,
    NoHeaderException,
    NoRefreshTokenException,
)
from src.services.auth import AuthService

router = APIRouter()


@router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    description="Login via username and password",
    summary="This endpoint returns access token and sets csrf token and refresh token in cookies",
    responses={
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
        raise NoHeaderException("Invalid request")

    tokens = await auth_service.login(
        username=creds.username, password=creds.password, device_id=device_id
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
    status_code=status.HTTP_201_CREATED,
    description="Refresh tokens",
    summary="This endpoint returns new access token and sets csrf token and new refresh token in cookies",
    responses={
        status.HTTP_201_CREATED: {"model": AccessToken},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ValidationErrorResponse
        },
    },
)
async def refresh(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    csrf_cookie: str = Cookie(None, alias="csrf_token"),
    refresh_token: str = Cookie(None, alias="refresh_token"),
    csrf_header: str | None = Header(None, alias="X-CSRF-Token"),
    device_id: str | None = Header(None, alias="X-Device-ID"),
) -> AccessToken:
    if not device_id:
        raise NoHeaderException("Invalid request")

    if not refresh_token:
        raise NoRefreshTokenException(
            "Invalid request data, please login firstly"
        )

    if not csrf_header or csrf_header != csrf_cookie:
        raise NoCsrfTokenException("Invalid request")

    new_token_pair = await auth_service.refresh_token(refresh_token, device_id)
    response.set_cookie(
        key="refresh_token",
        value=new_token_pair.refresh_token,
        httponly=True,
        secure=False,
        samesite="strict",
    )
    return AccessToken(access_token=new_token_pair.access_token)


@router.post(
    path="/logout",
    status_code=status.HTTP_200_OK,
    description="Logout from the system with device id",
    summary="This endpoint deletes refresh token with specified device id and csrf token from cookies",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid token"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ValidationErrorResponse
        },
    },
)
async def logout(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    current_user: Annotated[UserReturnSchema, Depends(get_current_user)],
    csrf_cookie: str = Cookie(None, alias="csrf_token"),
    csrf_header: str | None = Header(None, alias="X-CSRF-Token"),
    device_id: str | None = Header(None, alias="X-Device-ID"),
) -> LogoutResponse:
    if not device_id:
        raise NoHeaderException("Invalid request")

    if not csrf_header or csrf_header != csrf_cookie:
        raise NoCsrfTokenException("Invalid request")

    response.delete_cookie("refresh_token")
    response.delete_cookie("csrf_token")

    tokens_revoked = await auth_service.logout(current_user.email, device_id)
    return LogoutResponse(
        message="Logged out successfully", tokens_revoked=tokens_revoked
    )


@router.post(
    path="/logout_all",
    status_code=status.HTTP_200_OK,
    description="Logout from all devices",
    summary="This endpoint deletes all refresh tokens with specified email and csrf token from cookies",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid token"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ValidationErrorResponse
        },
    },
)
async def logout_all(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    current_user: Annotated[UserReturnSchema, Depends(get_current_user)],
    csrf_cookie: str = Cookie(None, alias="csrf_token"),
    csrf_header: str | None = Header(None, alias="X-CSRF-Token"),
    device_id: str | None = Header(None, alias="X-Device-ID"),
) -> LogoutResponse:
    if not device_id:
        raise NoHeaderException("Invalid request")

    if not csrf_header or csrf_header != csrf_cookie:
        raise NoCsrfTokenException("Invalid request")

    tokens_revoked = await auth_service.logout_all(current_user.email)
    return LogoutResponse(
        message="Logged out from all devices", tokens_revoked=tokens_revoked
    )
