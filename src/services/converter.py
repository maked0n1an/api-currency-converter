from typing import List

from httpx import AsyncClient

from src.api.schemas.currency import CurrencyInfo
from src.core.config import currency_api_settings


class ConverterService:
    def __init__(self):
        self.api_url = currency_api_settings.API_URL
        self.async_client = AsyncClient()

    async def get_available_symbols(self) -> List[CurrencyInfo]:
        response = await self.async_client.get(url=f"{self.api_url}/tickers/")
        data = response.json()
        return [
            CurrencyInfo(symbol=currency["symbol"], name=currency["name"])
            for currency in data["data"]
        ]

    async def convert_currency(
        self, from_symbol: str, to_symbols: List[str], amount: float = 1.0
    ) -> dict[str, float]:
        available_currencies = await self.async_client.get(
            url=f"{self.api_url}/tickers/"
        )
        currencies_data = available_currencies.json()["data"]

        to_symbols.append(from_symbol)
        currency_ids = [
            currency["id"]
            for currency in currencies_data
            if currency["symbol"] in to_symbols
        ]
        currency_ids_query = ",".join(currency_ids)

        currency_rates_response = await self.async_client.get(
            url=f"{self.api_url}/ticker/", params={"id": currency_ids_query}
        )
        currency_rates_data = currency_rates_response.json()
        for currency_info in currency_rates_data:
            if currency_info["symbol"] == from_symbol:
                base_currency_rate = float(currency_info["price_usd"])
                break

        conversion_rates: dict[str, float] = {
            currency["symbol"]: round(
                base_currency_rate * amount / float(currency["price_usd"]), 8
            )
            for currency in currency_rates_data
            if currency["symbol"] != from_symbol
        }
        return conversion_rates
