from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.schemas._common import ValidationErrorDetail, ValidationErrorResponse
from src.exceptions.services import (
    AuthException,
    NoHeaderException,
    TokenException,
    UserAlreadyExistsException,
    UserException,
    UserNotAuthorizedException,
    UserNotFoundException,
    WrongAuthorizationHeaderException,
)


async def auth_exception_handler(request: Request, exc: AuthException):
    exc_codes = {
        NoHeaderException: status.HTTP_400_BAD_REQUEST,
    }
    status_code = exc_codes.get(type(exc), status.HTTP_401_UNAUTHORIZED)
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
    )


async def token_exception_handler(request: Request, exc: TokenException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
    )


async def user_exception_handler(request: Request, exc: UserException):
    exc_codes = {
        WrongAuthorizationHeaderException: status.HTTP_401_UNAUTHORIZED,
        UserNotAuthorizedException: status.HTTP_401_UNAUTHORIZED,
        UserNotFoundException: status.HTTP_404_NOT_FOUND,
        UserAlreadyExistsException: status.HTTP_409_CONFLICT,
    }

    status_code = exc_codes.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(
        status_code=status_code, content={"detail": exc.message}
    )


async def custom_request_validation_handler(
    request: Request, err: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ValidationErrorResponse(
            details=[
                ValidationErrorDetail(
                    type=err["type"],
                    field=err["loc"][-1],
                    message=err["msg"],
                    input=err["input"],
                )
                for err in err.errors()
            ]
        ).model_dump(),
    )
