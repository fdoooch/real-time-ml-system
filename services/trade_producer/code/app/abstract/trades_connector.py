from abc import ABC, abstractmethod
from typing import Callable


class TradesConnector(ABC):
	@abstractmethod
	def __init__(self): ...

	@abstractmethod
	def subscribe_to_trades(self, symbols: list[str], callback_handler: Callable) -> None: ...
