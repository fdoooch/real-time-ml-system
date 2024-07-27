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
	URL = "wss://fstream.binance.com"
	# wss://fstream.binance.com/stream?streams=bnbusdt@aggTrade/btcusdt@markPrice

	def __init__(self):
		self._ws = None
		# self._ws = self._subscribe_to_trades()

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
			symbol=symbols[0],
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
		

	# def get_trades(self) -> list[Dict]:
	# 	msg = self._ws.recv()
	# 	print(f"Received message: {msg}")
	# 	if '"heartbeat"' in msg:
	# 		return []
	# 	msg_json = json.loads(msg)
	# 	if msg_json.get("channel") == "trade":
	# 		trades = []
	# 		for trade in msg_json.get("data"):
	# 			trades.append(
	# 				{
	# 					"symbol": trade.get("symbol"),
	# 					"price": trade.get("price"),
	# 					"qty": trade.get("qty"),
	# 					"timestamp": convert_datetime_to_timestamp_in_ms(
	# 						trade.get("timestamp")
	# 					),
	# 				}
	# 			)
	# 		return trades
	# 	print("Unknown websocket message format")
	# 	return msg
