from pydantic import BaseModel


class UserCredsSchema(BaseModel):
    username: str
    password: str


class AccessToken(BaseModel):
    token_scheme: str = "Bearer"
    access_token: str


class AuthTokenPair(AccessToken):
    refresh_token: str


class JwtTokenCreate(BaseModel):
    id: str
    token_type: str
    email: str
    device_id: str | None
