import uvicorn
from fastapi import FastAPI

from src.api.endpoints.auth import router as auth_router
from src.api.endpoints.user import router as user_router
from src.api.middleware.handlers import (
    auth_exception_handler,
    token_exception_handler,
    user_exception_handler,
)
from src.exceptions.services import (
    AuthException,
    TokenException,
    UserException,
)

app = FastAPI(title="API CryptoCurrency Converter")

app.add_exception_handler(AuthException, auth_exception_handler)
app.add_exception_handler(TokenException, token_exception_handler)
app.add_exception_handler(UserException, user_exception_handler)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/user", tags=["User"])

if __name__ == "__main__":
    uvicorn.run(app=app, port=8000)
