from src.exceptions._common import GenericException


class CurrencyRouterException(GenericException):
    """Base exception for currency-related errors"""

    pass


class InvalidSymbolException(CurrencyRouterException):
    pass
