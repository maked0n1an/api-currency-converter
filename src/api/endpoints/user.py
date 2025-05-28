from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.dependencies.dependencies import (
    get_current_user,
    get_user_service,
)
from src.api.schemas._common import ValidationErrorResponse
from src.api.schemas.user import (
    UserRegisterResponse,
    UserRegisterSchema,
    UserReturnSchema,
    UserUpdateSchema,
)
from src.services.user import UserService

router = APIRouter()


@router.post(
    path="/register",
    status_code=status.HTTP_201_CREATED,
    description="Register using username and password",
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ValidationErrorResponse
        },
    },
)
async def register(
    user_data: UserRegisterSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRegisterResponse:
    return await user_service.add_user(user_data)


@router.put(
    path="/complete_profile",
    description="Add user info like name and surname",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid token"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ValidationErrorResponse
        },
    },
)
async def complete_profile(
    user_data: UserUpdateSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserReturnSchema, Depends(get_current_user)],
) -> UserReturnSchema:
    return await user_service.update_user(
        user_id=current_user.id, profile_data=user_data
    )


@router.get(
    path="/about_me",
    description="Get info about authenticated user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid token"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def get_user_info(
    current_user: Annotated[UserReturnSchema, Depends(get_current_user)],
) -> UserReturnSchema:
    return current_user
