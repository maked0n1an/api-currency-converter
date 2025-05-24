from typing import Literal
from dotenv import find_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseModel):
    dialect: str = Field(default='postgres')
    async_driver: str = Field(default="asyncpg")
    sync_driver: str = Field(default="psycopg2")

    USER: str
    PASS: str
    HOST: str
    PORT: int
    NAME: str

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


class JwtSettings(BaseModel):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRES_MINUTES: int
    REFRESH_TOKEN_EXPIRES_DAYS: int
    ALGORITHM: Literal['HS256', 'RS256', 'PS256', 'EdDSA', 'ES256'] = Field(
        default='HS256',
        description='One of digital signature algorithms for decoding/encoding JWT'
    )


class CurrencySettings(BaseModel):
    API_URL: str
    API_KEY: str


class Settings(BaseSettings):
    db: DbSettings
    jwt: JwtSettings
    currency: CurrencySettings

    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_nested_delimiter="_",
        env_nested_max_split=1
    )


settings = Settings()
