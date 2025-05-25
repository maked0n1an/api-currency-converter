from typing_extensions import TypedDict
import uuid

from pydantic import BaseModel


class UserRegisterSchema(BaseModel):
    email: str
    username: str
    password: str


class UserUpdateSchema(BaseModel):
    first_name: str
    last_name: str


class UserReturnSchema(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    first_name: str | None
    last_name: str | None


class UserRegisterResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str


class ExternalAuthUserCreateSchema(BaseModel):
    email: str
    first_name: str
    last_name: str
    

class UserFilter(TypedDict):
    email: str
    username: str
    

class GoogleUserCreateSchema(ExternalAuthUserCreateSchema):
    pass
