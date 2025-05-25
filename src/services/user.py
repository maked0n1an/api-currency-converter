from uuid import UUID

from sqlalchemy import or_

from src.api.schemas.user import (
    UserRegisterSchema,
    UserReturnSchema,
    UserUpdateSchema,
)
from src.utils.password import PasswordHasher
from src.utils.unit_of_work import IUnitOfWork


class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_user(self, user: UserRegisterSchema) -> UserReturnSchema:
        async with self.uow as uow:
            hashed_password = PasswordHasher.hash(user.password)
            user_data = {
                **user.model_dump(exclude={"password"}),
                "hashed_password": hashed_password,
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

    async def find_by_username_or_email(
        self, username: str | None, email: str | None
    ) -> UserReturnSchema | None:
        async with self.uow as uow:
            conditions = []
            if username:
                conditions.append(uow.user.model.username == username)
            if email:
                conditions.append(uow.user.model.email == email)

            or_filter = or_(*conditions)
            if result := await uow.user.get_user_by_expression(or_filter):
                return UserReturnSchema.model_validate(
                    result, from_attributes=True
                )
