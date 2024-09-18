import datetime
import logging
from typing import Callable, Dict

from pybit.unified_trading import WebSocket

from app.abstract import TradesConnector
from app.config import settings
from app.schemas.trade_schema import Trade

logger = logging.getLogger(settings.LOGGER_NAME)


def convert_datetime_to_timestamp_in_ms(dt_str: str) -> int:
	dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
	# Convert to Unix timestamp in milliseconds
	timestamp_ms = int(dt.timestamp() * 1000)
	return timestamp_ms


class BybitSpotTradesConnector(TradesConnector):

	def __init__(self):
		self._ws: WebSocket = None

	def subscribe_to_trades(self, symbols: list[str], callback_handler: Callable) -> None:
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
		self.callback_handler = callback_handler
		return None
	
	def _callback_handler(self, msg: Dict) -> list[Dict]:
		logger.debug(msg)

		trades = []
		for item in msg.get("data"):
			logger.debug(item)	
			trade = Trade(
				symbol=item.get("s"),
				price=item.get("p"),
				qty=item.get("q"),
				timestamp_ms=item.get("T"),
			)
			trades.append(trade)
		self.callback_handler(trades)
