from pydantic import BaseModel, Field


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


class JwtTokenFilter(BaseModel):
    email: str
    is_revoked: bool
    device_id: str | None = None


class LogoutResponse(BaseModel):
    message: str
    tokens_revoked: int = Field(..., description="Number of tokens revoked")
