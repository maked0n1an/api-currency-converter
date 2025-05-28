import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.api.endpoints.auth import router as auth_router
from src.api.endpoints.converter import router as converter_router
from src.api.endpoints.user import router as user_router
from src.api.middleware.handlers import (
    auth_exception_handler,
    currency_exception_handler,
    custom_request_validation_handler,
    token_exception_handler,
    user_exception_handler,
)
from src.exceptions.routers import CurrencyRouterException
from src.exceptions.services import (
    AuthServiceException,
    TokenServiceException,
    UserServiceException,
)

app = FastAPI(title="API CryptoCurrency Converter")

app.add_exception_handler(AuthServiceException, auth_exception_handler)
app.add_exception_handler(TokenServiceException, token_exception_handler)
app.add_exception_handler(UserServiceException, user_exception_handler)
app.add_exception_handler(CurrencyRouterException, currency_exception_handler)
app.add_exception_handler(
    RequestValidationError, custom_request_validation_handler
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(converter_router, prefix="/currency", tags=["Converter"])

if __name__ == "__main__":
    uvicorn.run(app=app, port=8000)
