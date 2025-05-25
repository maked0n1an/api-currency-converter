from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.dependencies.dependencies import (
    get_current_user,
    get_user_service,
)
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
    summary="Register using username and password",
)
async def register(
    user_data: UserRegisterSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRegisterResponse:
    return await user_service.add_user(user_data)


@router.put(
    path="/complete_profile",
    summary="Add user info like name and surname",
    responses={
        status.HTTP_200_OK: {"model": UserReturnSchema},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid data provided"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
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
    summary="Get info about authenticated user",
    responses={
        status.HTTP_200_OK: {"model": UserReturnSchema},
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def get_user_info(
    current_user: Annotated[UserReturnSchema, Depends(get_current_user)],
) -> UserReturnSchema:
    return current_user
