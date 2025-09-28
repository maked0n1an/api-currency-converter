import datetime
import uuid
from enum import Enum

import jwt
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing_extensions import TypedDict

from src.core.config import jwt_settings

access_token_header = APIKeyHeader(
    name="Authorization",
    description="The headers should contain 'Authorization' with 'bearer'\ scheme",
    auto_error=False,
    scheme_name="AccessToken",
)


class TokenTypeEnum(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class JwtDataToEncode(TypedDict):
    sub: str
    device_id: str


class JwtPayload(BaseModel):
    jti: str
    sub: str
    exp: datetime.datetime
    iat: datetime.datetime
    typ: str
    device_id: str


class JwtAuth:
    @staticmethod
    def create_payload(
        sub: str,
        device_id: str,
        token_type: TokenTypeEnum
    ) -> JwtPayload:
        current_time = datetime.datetime.now(datetime.timezone.utc)

        if token_type == TokenTypeEnum.ACCESS:
            expire_delta = datetime.timedelta(
                minutes=jwt_settings.ACCESS_TOKEN_EXPIRES_MINUTES
            )
        elif token_type == TokenTypeEnum.REFRESH:
            expire_delta = datetime.timedelta(
                days=jwt_settings.REFRESH_TOKEN_EXPIRES_DAYS
            )
        else:
            raise ValueError(f"Unsupported token type: {token_type}")

        return JwtPayload(
            jti=str(uuid.uuid4()),
            sub=sub,
            exp=current_time + expire_delta,
            iat=current_time,
            typ=token_type,
            device_id=device_id,
        )

    @staticmethod
    def create_token(payload: JwtPayload) -> str:
        token = jwt.encode(
            payload=payload.model_dump(),
            key=jwt_settings.SECRET_KEY,
            algorithm=jwt_settings.ALGORITHM,
        )
        return token

    @staticmethod
    def decode_token(token: str, verify_exp: bool = False) -> JwtPayload:
        try:
            payload: dict = jwt.decode(
                jwt=token,
                key=jwt_settings.SECRET_KEY,
                algorithms=[jwt_settings.ALGORITHM],
                options={"verify_exp": verify_exp},
                leeway=0,
            )
            return JwtPayload(**payload)
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
