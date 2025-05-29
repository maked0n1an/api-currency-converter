import pytest
from httpx import AsyncClient
from src.api.schemas.currency import CurrencyInfo


@pytest.mark.asyncio
async def test_get_currency_list(client: AsyncClient, authed_user, monkeypatch):
    currencies = [
        CurrencyInfo(symbol="BTC", name="Bitcoin"),
        CurrencyInfo(symbol="ETH", name="Ethereum"),
        CurrencyInfo(symbol="USDT", name="Tether Dollar U.S.")
    ]
    client.cookies = authed_user["cookies"]
    client.headers = authed_user["headers"]

    async def fake_get_available(self):
        return currencies

    monkeypatch.setattr(
        "src.services.converter.ConverterService.get_available_symbols",
        fake_get_available,
    )

    response = await client.get("/currency/list")
    data = response.json()["currencies"]

    assert response.status_code == 200
    assert isinstance(data, list)
    for i, currency in enumerate(data):
        assert currency["symbol"] == currencies[i].symbol
        assert currency["name"] == currencies[i].name


@pytest.mark.asyncio
async def test_convert_success(client: AsyncClient, authed_user, monkeypatch):
    currencies = (
        CurrencyInfo(symbol="ETH", name="Ethereum"),
        CurrencyInfo(symbol="BTC", name="Bitcoin"),
        CurrencyInfo(symbol="USDT", name="Tether Dollar U.S."),
        CurrencyInfo(symbol="DOGE", name="Dogecoin"),
    )
    client.headers = authed_user["headers"]
    client.cookies = authed_user["cookies"]

    async def fake_get_available(self):
        return currencies

    async def fake_convert(self, from_symbol, to_symbols, amount):
        return {
            "BTC": 0.03625336,
            "USDT": 3944.025,
            "DOGE": 17680.02671711
        }

    monkeypatch.setattr(
        "src.services.converter.ConverterService.get_available_symbols",
        fake_get_available,
    )
    monkeypatch.setattr(
        "src.services.converter.ConverterService.convert_currency",
        fake_convert,
    )

    payload = {
        "from_symbol": "ETH",
        "to_symbols": ["BTC", "USDT", "DOGE"],
        "amount": "1.5"
    }
    response = await client.post("/currency/convert", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["from_symbol"] == "ETH"
    assert data["amount"] == 1.5
    assert "rates" in data
    assert data["rates"]["BTC"] == 0.03625336
    assert data["rates"]["USDT"] == 3944.025
    assert data["rates"]["DOGE"] == 17680.02671711


@pytest.mark.asyncio
async def test_convert_invalid_from_symbol(client: AsyncClient, authed_user, monkeypatch):
    currencies = [CurrencyInfo(symbol="ETH", name="Ethereum")]
    client.headers = authed_user["headers"]
    client.cookies = authed_user["cookies"]

    async def fake_get_available(self):
        return currencies

    monkeypatch.setattr(
        "src.services.converter.ConverterService.get_available_symbols",
        fake_get_available,
    )

    payload = {
        "from_symbol": "USDT",
        "to_symbols": ["ETH"],
        "amount": 3000
    }
    response = await client.post("/currency/convert", json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid 'from' symbol: 'USDT'"}


@pytest.mark.asyncio
async def test_convert_invalid_to_symbols(client: AsyncClient, authed_user, monkeypatch):
    currencies = [CurrencyInfo(symbol="USDT", name="Tether Dollar U.S.")]
    client.headers = authed_user["headers"]
    client.cookies = authed_user["cookies"]

    async def fake_get_available(self):
        return currencies

    monkeypatch.setattr(
        "src.services.converter.ConverterService.get_available_symbols",
        fake_get_available,
    )
    payload = {
        "from_symbol": "USDT",
        "to_symbols": ["ETH"],
        "amount": 3000
    }
    response = await client.post("/currency/convert", json=payload)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid 'to' currencies: ['ETH'], check the available symbols"}


@pytest.mark.asyncio
async def test_convert_invalid_unauthed_user(client: AsyncClient, monkeypatch):
    currencies = [CurrencyInfo(symbol="USDT", name="Tether Dollar U.S.")]

    async def fake_get_available(self):
        return currencies

    monkeypatch.setattr(
        "src.services.converter.ConverterService.get_available_symbols",
        fake_get_available,
    )
    payload = {
        "from_symbol": "ETH",
        "to_symbols": ["USDT"],
        "amount": 1.5
    }
    response = await client.post("/currency/convert", json=payload)

    assert response.status_code == 401
    assert response.json() == {'detail': 'No Authorization header received'}
