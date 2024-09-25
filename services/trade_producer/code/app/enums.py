from enum import Enum


class TradeSourceName(Enum):
    KRAKEN_SPOT = "kraken_spot"
    KRAKEN_SPOT_HISTORICAL = "kraken_spot_historical"
    BYBIT_SPOT = "bybit_spot"
