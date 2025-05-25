# auth exceptions
class AuthException(Exception):
    """Base exception for auth-related errors"""

    def __init__(self, message: str):
        self.message = message


class TokenException(AuthException):
    """Base exception for token-related errors"""

    pass


class TokenExpiredException(TokenException):
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)


class InvalidTokenException(TokenException):
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


class WrongTokenTypeException(TokenException):
    """Raised when token type doesn't match expected type"""

    def __init__(self, message: str = "Wrong token type exception"):
        super().__init__(message)


class RevokedTokenException(TokenException):
    """Raise when token has been revoked"""

    def __init__(self, message: str = "Token has been revoked"):
        super().__init__(message)


class NoRefreshTokenException(TokenException):
    """Raise when no refresh token is in cookies"""

    def __init__(self, message: str = "No refresh token provided"):
        super().__init__(message)


class NoCrsfTokenException(TokenException):
    """Raise when no CSRF token is in cookies"""

    def __init__(self, message: str = "No CSRF-token provided"):
        super().__init__(message)


# user exceptions
class UserException(Exception):
    """Base exception for user-related errors"""

    def __init__(self, message: str):
        self.message = message


class UserNotAuthorizedException(UserException):
    def __init__(self, message: str = "User not authorized"):
        super().__init__(message)


class UserAlreadyExistsException(UserException):
    def __init__(self, message: str = "User already exists"):
        super().__init__(message)


class UserNotFoundException(UserException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message)


class WrongAuthorizationHeaderException(AuthException):
    def __init__(self, message: str = "Wrong authorization header"):
        self.message = message
