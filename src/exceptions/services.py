from src.exceptions._common import GenericException


# auth exceptions
class AuthServiceException(GenericException):
    """Base exception for auth-related errors"""

    pass


class NoHeaderException(AuthServiceException):
    pass


class WrongAuthorizationHeaderException(AuthServiceException):
    def __init__(self, message: str = "Wrong authorization header"):
        super().__init__(message)


class TokenServiceException(GenericException):
    """Base exception for token-related errors"""

    pass


class TokenExpiredException(TokenServiceException):
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)


class InvalidTokenException(TokenServiceException):
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


class WrongTokenTypeException(TokenServiceException):
    def __init__(self, message: str = "Wrong token type exception"):
        super().__init__(message)


class RevokedTokenException(TokenServiceException):
    def __init__(self, message: str = "Token has been revoked"):
        super().__init__(message)


class NoRefreshTokenException(TokenServiceException):
    """Raise when no refresh token is in cookies"""

    def __init__(self, message: str = "No refresh token provided"):
        super().__init__(message)


class NoCsrfTokenException(TokenServiceException):
    """Raise when no CSRF token is in cookies"""

    def __init__(self, message: str = "No CSRF-token provided"):
        super().__init__(message)


# user exceptions
class UserServiceException(GenericException):
    """Base exception for user-related errors"""

    pass


class UserNotAuthorizedException(UserServiceException):
    def __init__(self, message: str = "User not authorized"):
        super().__init__(message)


class UserAlreadyExistsException(UserServiceException):
    def __init__(self, message: str = "User already exists"):
        super().__init__(message)


class UserNotFoundException(UserServiceException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message)
