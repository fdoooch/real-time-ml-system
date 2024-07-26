import datetime
import json
import logging
from typing import Dict

from websocket import WebSocket, create_connection

from src.abstract.trade_producer import TradeProducer
from src.config import config

logger = logging.getLogger(config.LOGGER_NAME)


def convert_datetime_to_timestamp_in_ms(dt_str: str) -> int:
	dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
	# Convert to Unix timestamp in milliseconds
	timestamp_ms = int(dt.timestamp() * 1000)
	return timestamp_ms


class KrakenTradeProducer(TradeProducer):
	URL = "wss://ws.kraken.com/v2"

	def __init__(self):
		self._ws = None
		# self._ws = self._subscribe_to_trades()

	def subscribe_to_trades(self, symbols: list[str]) -> None:
		"""
		Establishes a connection to the Kraken websocket API
		"""
		symbols = [f"{symbol.split('USDT')[0]}/USDT" for symbol in symbols]
		self._ws = create_connection(self.URL)
		# subscribe to trades
		msg = {
			"method": "subscribe",
			"params": {
				"channel": "trade",
				"symbol": symbols,
				"snapshot": False,
			},
		}
		self._ws.send(json.dumps(msg))

		# wait for subscription confirmation
		for i in range(len(symbols) + 1):
			msg = self._ws.recv()
			logger.debug(f"Received message: {msg}")
			msg_json = json.loads(msg)
			if msg_json.get("method") == "subscribe" and msg_json.get("success"):
				logger.info(f"Subscribed to {msg_json.get('result').get('symbol')}")
		return None

	def get_trades(self) -> list[Dict]:
		msg = self._ws.recv()
		print(f"Received message: {msg}")
		if '"heartbeat"' in msg:
			return []
		msg_json = json.loads(msg)
		if msg_json.get("channel") == "trade":
			trades = []
			for trade in msg_json.get("data"):
				trades.append(
					{
						"symbol": trade.get("symbol"),
						"price": trade.get("price"),
						"qty": trade.get("qty"),
						"timestamp": convert_datetime_to_timestamp_in_ms(
							trade.get("timestamp")
						),
					}
				)
			return trades
		print("Unknown websocket message format")
		return msg
