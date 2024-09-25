import datetime
import logging
from typing import Callable, Dict

from app.abstract import TradesConnector
from app.config import settings
from app.schemas.trade_schema import Trade
from pybit.unified_trading import WebSocket

logger = logging.getLogger(settings.LOGGER_NAME)


def convert_datetime_to_timestamp_in_ms(dt_str: str) -> int:
	dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
	# Convert to Unix timestamp in milliseconds
	timestamp_ms = int(dt.timestamp() * 1000)
	return timestamp_ms


class BybitSpotTradesConnector(TradesConnector):
	_is_active: bool # is connector produce any trades or not

	@property
	def is_active(self) -> bool:
		return self._is_active

	def __init__(self):
		self._ws: WebSocket = None
		self._is_active = False

	def subscribe_to_trades(
		self,
        symbols: list[str],
        callback: Callable = None,
        start_unix_epoch_ms: int | None = None,
        end_unix_epoch_ms: int | None = None,
	) -> None:
		"""
		Establishes a connection to the Bybit websocket API
		"""
		self._ws = WebSocket(
			testnet=False,
			channel_type="spot",
		)
		# subscribe to trades
		self._ws.trade_stream(
			symbol=symbols,
			callback=self._callback_handler,
		)
		self.callback_handler = callback
		self._is_active = True
		return None
	
	def _callback_handler(self, msg: Dict) -> list[Dict]:
		logger.debug(msg)

		trades = []
		for item in msg.get("data"):
			logger.debug(item)	
			trade = Trade(
				symbol=item.get("s"),
				price=item.get("p"),
				qty=item.get("v"),
				timestamp_ms=item.get("T"),
			)
			trades.append(trade)
		self.callback_handler(trades)
