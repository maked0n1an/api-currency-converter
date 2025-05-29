from typing import List

from pydantic import BaseModel, Field


class CurrencyInfo(BaseModel):
    symbol: str = Field(
        description="Currency symbol", examples=["ETH", "BTC", "USDT", "DOGE"]
    )
    name: str = Field(
        description="Currency name",
        examples=["Ethereum", "Bitcoin", "Tether", "Dogecoin"],
    )


class CurrencyListResponse(BaseModel):
    currencies: List[CurrencyInfo] = Field(description="List of currencies")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "currencies": [
                        {"symbol": "ETH", "name": "Ethereum"},
                        {"symbol": "BTC", "name": "Bitcoin"},
                        {"symbol": "USDT", "name": "Tether"},
                        {"symbol": "DOGE", "name": "Dogecoin"},
                    ]
                }
            ]
        }
    }


class ConvertRequest(BaseModel):
    from_symbol: str = Field(description="Currency symbol to convert from")
    amount: float = Field(default=1, gt=0, description="Amount to convert")
    to_symbols: List[str] = Field(
        description="Currencies symbols to convert to"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "from_symbol": "ETH",
                    "amount": 1.5,
                    "to_symbols": ["BTC", "USDT", "DOGE"],
                }
            ]
        }
    }


class ConvertRatesResponse(BaseModel):
    from_symbol: str = Field(
        description="Currency symbol to convert from", examples=["ETH"]
    )
    amount: float = Field(description="Amount to convert", examples=[1.5])
    rates: dict[str, float] = Field(
        description="Rates of conversion",
        examples=[
            {
                "BTC": 0.03625336,
                "USDT": 3944.025,
                "DOGE": 17680.02671711,
            }
        ],
    )
