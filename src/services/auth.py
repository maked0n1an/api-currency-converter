import secrets

from src.api.schemas.auth import AuthTokenPair, JwtTokenCreate, JwtTokenFilter
from src.api.schemas.user import UserReturnSchema
from src.core.security import JwtAuth, TokenTypeEnum
from src.exceptions.services import (
    InvalidTokenException,
    RevokedTokenException,
    TokenExpiredException,
    UserNotAuthorizedException,
    WrongTokenTypeException,
)
from src.utils.password import PasswordHasher
from src.utils.unit_of_work import IUnitOfWork


class AuthService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def login(
        self, username: str, password: str, device_id: str
    ) -> AuthTokenPair:
        db_user = await self._authenticate_user(username, password)
        return await self._get_new_token_pair(db_user.email, device_id)

    async def logout(self, email: str, device_id: str) -> int:
        filters = JwtTokenFilter(
            email=email, device_id=device_id, is_revoked=False
        )
        return await self._logout(filters.model_dump(exclude_none=True))

    async def logout_all(self, email: str) -> int:
        filters = JwtTokenFilter(email=email, is_revoked=False)
        return await self._logout(filters.model_dump(exclude_none=True))

    async def refresh_token(
        self, refresh_token: str, device_id: str
    ) -> AuthTokenPair:
        decoded_payload = await self.verify_token_and_type(
            refresh_token, TokenTypeEnum.REFRESH
        )
        async with self.uow as uow:
            is_revoked = await uow.jwt_token.is_token_revoked(
                decoded_payload.jti
            )

            if is_revoked is None:
                raise InvalidTokenException()

            if is_revoked:
                raise RevokedTokenException()

        return await self._get_new_token_pair(decoded_payload.sub, device_id)

    async def verify_token_and_type(
        self, token: str, expected_type: TokenTypeEnum, verify_exp: bool = True
    ):
        try:
            decoded_payload = JwtAuth.decode_token(token, verify_exp)
        except ValueError as e:
            err = str(e)
            if "expired" in err:
                raise TokenExpiredException(str(err))
            raise InvalidTokenException(str(err))

        if decoded_payload.typ != expected_type:
            raise WrongTokenTypeException(
                f"Expected {expected_type}, got {decoded_payload.typ}"
            )

        return decoded_payload

    async def _logout(self, filters: dict) -> int:
        async with self.uow as uow:
            affected_tokens = await uow.jwt_token.revoke_tokens(filters)
            await uow.commit()
            return affected_tokens

    async def _authenticate_user(
        self, username: str, password: str
    ) -> UserReturnSchema:
        async with self.uow as uow:
            db_user = await uow.user.get_user({"username": username})

            if not db_user:
                raise UserNotAuthorizedException(
                    "Invalid username or password"
                )

            current_username_digest = username.encode()
            correct_username_digest = db_user.username.encode()

            is_username_correct = secrets.compare_digest(
                current_username_digest, correct_username_digest
            )
            is_password_correct = PasswordHasher.verify(
                password, db_user.hashed_password
            )
            if not (is_username_correct and is_password_correct):
                raise UserNotAuthorizedException(
                    "Invalid username or password"
                )
            return UserReturnSchema.model_validate(
                db_user, from_attributes=True
            )

    async def _get_new_token_pair(
        self,
        email: str,
        device_id: str,
    ) -> AuthTokenPair:
        refresh_payload = JwtAuth.create_payload(
            email, device_id, TokenTypeEnum.REFRESH
        )

        async with self.uow as uow:
            filters = {"email": email, "device_id": device_id}
            await uow.jwt_token.revoke_tokens(filters)

            db_token = JwtTokenCreate(
                id=refresh_payload.jti,
                token_type=refresh_payload.typ,
                email=refresh_payload.sub,
                device_id=refresh_payload.device_id,
            )
            await uow.jwt_token.add_token(db_token.model_dump())
            await uow.commit()

        access_payload = JwtAuth.create_payload(
            email, device_id, TokenTypeEnum.ACCESS
        )
        return AuthTokenPair(
            access_token=JwtAuth.create_token(access_payload), 
            refresh_token=JwtAuth.create_token(refresh_payload)
        )
