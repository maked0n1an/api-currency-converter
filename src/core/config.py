from typing import Literal

from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class DbSettings(BaseSettings):
    dialect: str = Field(default="postgresql")
    async_driver: str = Field(default="asyncpg")

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_HOST: str
    TEST_DB_PORT: str
    TEST_DB_NAME: str

    PREPARE_DB: Literal["PROD", "TEST"]

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"{self.dialect}+{self.async_driver}://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def TEST_DATABASE_URL(self) -> str:
        return (
            f"{self.dialect}+{self.async_driver}://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@"
            f"{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        )


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
