from pydantic import BaseModel


class Trade(BaseModel):
    symbol: str
    qty: float
    price: float
    timestamp_ms: int