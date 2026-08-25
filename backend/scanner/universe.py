from typing import Dict, List, Any

# Curated universe of liquid large-cap underlyings for options income overlay
UNIVERSE_CONFIG: List[Dict[str, Any]] = [
    {
        "symbol": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "sector": "Index ETF",
        "asset_type": "etf",
        "min_open_interest": 100,
        "max_spread_pct": 0.10,
    },
    {
        "symbol": "QQQ",
        "name": "Invesco QQQ Trust",
        "sector": "Tech Index ETF",
        "asset_type": "etf",
        "min_open_interest": 100,
        "max_spread_pct": 0.10,
    },
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "sector": "Information Technology",
        "asset_type": "stock",
        "min_open_interest": 50,
        "max_spread_pct": 0.12,
    },
    {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "sector": "Information Technology",
        "asset_type": "stock",
        "min_open_interest": 50,
        "max_spread_pct": 0.12,
    },
    {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "sector": "Semiconductors",
        "asset_type": "stock",
        "min_open_interest": 50,
        "max_spread_pct": 0.12,
    },
    {
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "sector": "Consumer Discretionary",
        "asset_type": "stock",
        "min_open_interest": 50,
        "max_spread_pct": 0.15,
    },
    {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "sector": "Consumer Discretionary / EV",
        "asset_type": "stock",
        "min_open_interest": 50,
        "max_spread_pct": 0.15,
    },
]

def get_curated_symbols() -> List[str]:
    return [item["symbol"] for item in UNIVERSE_CONFIG]

def get_symbol_metadata(symbol: str) -> Dict[str, Any]:
    for item in UNIVERSE_CONFIG:
        if item["symbol"].upper() == symbol.upper():
            return item
    return {
        "symbol": symbol.upper(),
        "name": symbol.upper(),
        "sector": "General Equities",
        "asset_type": "stock",
        "min_open_interest": 25,
        "max_spread_pct": 0.20,
    }
