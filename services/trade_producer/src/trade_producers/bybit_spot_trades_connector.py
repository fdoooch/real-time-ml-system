import datetime
import logging
from typing import Callable, Dict

from pybit.unified_trading import WebSocket

from src.abstract import TradesConnector
from src.config import config

logger = logging.getLogger(config.LOGGER_NAME)


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
		Establishes a connection to the Kraken websocket API
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
		logger.debug(type(msg))
		trades = []
		for item in msg.get("data"):
			logger.debug(item)	
			trade = {
				"symbol": item.get("s"),
				"price": item.get("p"),
				"qty": item.get("q"),
				"timestamp": item.get("T"),
			}
			trades.append(trade)
		self.callback_handler(trades)
