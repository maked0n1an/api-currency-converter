import re
import uuid

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ValidationInfo,
    field_validator,
)
from typing_extensions import TypedDict

PASSWORD_PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%\'^&*()_\-+=\[\]{}|\\;:"<>,./?~`]).{12,25}$'
)


class UserRegisterSchema(BaseModel):
    email: EmailStr = Field(...)
    username: str = Field(...)
    password: str = Field(
        min_length=12,
        max_length=25,
    )

    @field_validator("username")
    def validate_str(cls, value: str, info: ValidationInfo):
        if not value.isalpha():
            raise ValueError(
                f"{info.field_name.capitalize()} should contain only letters"
            )
        return value

    @field_validator("password")
    def validate_password(cls, value: str):
        if not PASSWORD_PATTERN.match(value):
            raise ValueError(
                "Password must be 12-25 characters long and contain uppercase, lowercase, digit, and special character"
            )
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "username": "thebestuser",
                    "password": "~BeMoreProactive71!",
                }
            ]
        }
    }


class UserUpdateSchema(BaseModel):
    first_name: str
    last_name: str

    @field_validator("first_name", "last_name")
    def validate_str(cls, value: str, info: ValidationInfo):
        parts = value.split("-")
        if not all(part.isalpha() for part in parts):
            raise ValueError(
                f"{info.field_name.capitalize()} should contain only letters"
            )
        return value


class UserReturnSchema(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    first_name: str | None
    last_name: str | None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "test@example.com",
                    "username": "testuser",
                    "first_name": "John",
                    "last_name": "Doe",
                }
            ]
        }
    }


class ExternalAuthUserCreateSchema(BaseModel):
    email: str
    first_name: str
    last_name: str


class UserRegisterResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "test@example.com",
                    "username": "testuser",
                }
            ]
        }
    }


class UserFilter(TypedDict):
    email: str
    username: str
