import logging

from passlib.context import CryptContext

logging.getLogger("passlib").setLevel(logging.ERROR)


class PasswordHasher:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def verify(cls, password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(password, hashed_password)
