from abc import ABC, abstractmethod
from typing import Dict


class TradeProducer(ABC):
	@abstractmethod
	def __init__(self): ...

	@abstractmethod
	def subscribe_to_trades(self, symbols: list[str]) -> None: ...

	@abstractmethod
	def get_trades(self) -> list[Dict]: ...
