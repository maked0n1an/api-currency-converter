from typing import Callable, Type
from uuid import UUID

from sqlalchemy import ColumnElement, or_

from src.api.schemas.user import (
    UserFilter,
    UserRegisterSchema,
    UserReturnSchema,
    UserUpdateSchema,
)
from src.db.database import Base
from src.db.models import User
from src.exceptions.services import UserAlreadyExistsException
from src.utils.password import PasswordHasher
from src.utils.unit_of_work import IUnitOfWork


class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_user(self, user: UserRegisterSchema) -> UserReturnSchema:
        where_clauses = self._build_get_filter_by_email_or_username(
            User, UserFilter(email=user.email, username=user.username)
        )
        async with self.uow as uow:
            result = await uow.user.get_user_by_expression(where_clauses)
            if result:
                raise UserAlreadyExistsException(
                    f"User with '{user.username}' username"
                    f" or '{user.email}' email exists"
                )

            user_data = {
                **user.model_dump(exclude={"password"}),
                "hashed_password": PasswordHasher.hash(user.password),
            }
            new_user = await uow.user.add_user(user_data)
            await uow.commit()
            return UserReturnSchema.model_validate(
                new_user, from_attributes=True
            )

    async def get_user(self, email: str) -> UserReturnSchema | None:
        async with self.uow as uow:
            if user := await uow.user.get_user({"email": email}):
                return UserReturnSchema.model_validate(
                    user, from_attributes=True
                )

    async def update_user(
        self, user_id: UUID, profile_data: UserUpdateSchema
    ) -> UserReturnSchema:
        async with self.uow as uow:
            updated_user = await uow.user.update_user(
                filters={"id": user_id},
                values=profile_data.model_dump(exclude_unset=True),
            )
            await uow.commit()
            return UserReturnSchema.model_validate(
                updated_user, from_attributes=True
            )

    def _build_get_filter_by_email_or_username(
        self, model: Type[Base], where_clauses: dict, operand: Callable = or_
    ) -> ColumnElement[bool]:
        conditions = []
        for key, value in where_clauses.items():
            if value is not None:
                conditions.append(getattr(model, key) == value)

        if not conditions:
            raise ValueError("At least one of attributes must be provided")
        return operand(*conditions)
