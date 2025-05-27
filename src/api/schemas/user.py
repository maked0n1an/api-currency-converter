import uuid

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator
from typing_extensions import TypedDict


class UserRegisterSchema(BaseModel):
    email: EmailStr = Field(..., description="Error in email")
    username: str = Field(..., description="Username should be string")
    password: str = Field(
        min_length=12,
        max_length=25,
        description="Password must be 12-25 characters long and contain uppercase, lowercase, digit, and special character",
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
        if not any(c.isupper() for c in value):
            raise ValueError(
                "Password should contain at least one uppercase letter"
            )

        if not any(c.islower() for c in value):
            raise ValueError(
                "Password should contain at least one lowercase letter"
            )

        if not any(c.isdigit() for c in value):
            raise ValueError("Password should contain at least one digit")

        special_chars = "!@#$%'^&*()_-+={}[|]\\;:\"<>,./?~`"
        if not any(c in special_chars for c in value):
            raise ValueError(
                "Password should contain at least one special character"
            )

        return value


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


class ExternalAuthUserCreateSchema(BaseModel):
    email: str
    first_name: str
    last_name: str


class UserRegisterResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str


class UserFilter(TypedDict):
    email: str
    username: str
