from typing import Annotated

from fastapi import APIRouter, Body, Depends, status

from src.api.dependencies.dependencies import (
    get_available_currencies,
    get_convert_service,
)
from src.api.schemas.currency import (
    ConvertRatesResponse,
    ConvertRequest,
    CurrencyListResponse,
)
from src.exceptions.routers import InvalidSymbolException
from src.services.converter import ConverterService

router = APIRouter()


@router.get(
    path="/list",
    description="Get list of available currencies like symbols and names",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid token"},
    },
)
async def get_currency_rates(
    currency_list=Depends(get_available_currencies),
) -> CurrencyListResponse:
    return currency_list


@router.post(
    path="/convert",
    description="Convert currency from one to many",
)
async def convert(
    convert: Annotated[ConvertRequest, Body()],
    currency_list: CurrencyListResponse = Depends(get_available_currencies),
    convert_service: ConverterService = Depends(get_convert_service),
) -> ConvertRatesResponse:
    available_symbols = [
        currency.symbol for currency in currency_list.currencies
    ]
    if convert.from_symbol not in available_symbols:
        raise InvalidSymbolException(
            f"Invalid 'from' symbol: '{convert.from_symbol}'"
        )

    invalid_to_symbols = [
        symbol
        for symbol in convert.to_symbols
        if symbol not in available_symbols
    ]
    if invalid_to_symbols:
        raise InvalidSymbolException(
            f"Invalid 'to' currencies: {invalid_to_symbols}, "
            "check the available symbols"
        )

    rates = await convert_service.convert_currency(
        from_symbol=convert.from_symbol,
        to_symbols=convert.to_symbols,
        amount=convert.amount,
    )
    return ConvertRatesResponse(
        from_symbol=convert.from_symbol, amount=convert.amount, rates=rates
    )
