from abc import ABC, abstractmethod
from typing import Callable


class TradesConnector(ABC):
	@abstractmethod
	def __init__(self): ...


	
	@property
	@abstractmethod
	def is_active(self) -> bool:
		raise NotImplementedError


	@abstractmethod
	def subscribe_to_trades(
		self, 
		symbols: list[str], 
		callback_handler: Callable,
		historical_start_ms: int | None = None,
        historical_end_ms: int | None = None,
	) -> None:
		raise NotImplementedError


