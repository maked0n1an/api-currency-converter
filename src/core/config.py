from typing import Literal

from dotenv import find_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    dialect: str = Field(default="postgresql")
    async_driver: str = Field(default="asyncpg")
    sync_driver: str = Field(default="psycopg2")

    USER: str
    PASS: str
    HOST: str
    PORT: int
    NAME: str

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="DB_", extra="ignore"
    )

    def _build_url(self, driver: str) -> str:
        return (
            f"{self.dialect}+{driver}://{self.USER}:{self.PASS}@"
            f"{self.HOST}:{self.PORT}/{self.NAME}"
        )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return self._build_url(self.async_driver)

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return self._build_url(self.sync_driver)


db_settings = DbSettings()


class JwtSettings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRES_MINUTES: int
    REFRESH_TOKEN_EXPIRES_DAYS: int
    ALGORITHM: Literal["HS256", "RS256", "PS256", "EdDSA", "ES256"] = Field(
        default="HS256",
        description="One of digital signature algorithms for decoding/encoding JWT",
    )

    model_config = SettingsConfigDict(
        env_file=find_dotenv(), env_prefix="JWT_", extra="ignore"
    )


jwt_settings = JwtSettings()


class CurrencyApiSettings(BaseSettings):
    API_URL: str

    model_config = SettingsConfigDict(
        env_file=find_dotenv(), env_prefix="CURRENCY_", extra="ignore"
    )


currency_api_settings = CurrencyApiSettings()
