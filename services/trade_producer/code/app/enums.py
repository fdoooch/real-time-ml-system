from enum import Enum


class TradeSourceName(Enum):
    KRAKEN = "kraken"
    KRAKEN_HISTORICAL = "kraken_historical"
    BYBIT_SPOT = "bybit_spot"
