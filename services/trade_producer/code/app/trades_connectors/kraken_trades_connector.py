import asyncio
import datetime
import json
import logging
from typing import Callable

import websockets
from app.abstract import TradesConnector
from app.config import settings
from app.schemas.trade_schema import Trade
from websockets import WebSocketClientProtocol

logger = logging.getLogger(settings.LOGGER_NAME)


def convert_datetime_to_timestamp_in_ms(dt_str: str) -> int:
    dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


class KrakenTradesConnector(TradesConnector):
	URL = "wss://ws.kraken.com/v2"

	def __init__(self):
		self._ws: WebSocketClientProtocol | None = None
		self._running = False  # Flag to control the message receiving loop

	async def connect(self) -> None:
		self._ws = await websockets.connect(self.URL)


	async def _receive_messages(self, callback: Callable):
		"""Handles receiving messages from the WebSocket."""
		try:
			while self._running:
				response = await self._ws.recv()
				msg_json = json.loads(response)

				if msg_json.get("channel") in ["status", "heartbeat"]:
					continue
				
				if msg_json.get("method") == "subscribe" and msg_json.get("success"):
					logger.info(f"Subscribed to {msg_json.get('result').get('symbol')}")
					continue

				logger.debug(f"Received message: {response}")

				# Call the callback function with the received message
				if callback:
					trades = self._extract_trades_from_websocket_message(msg_json)
					print(f"trades: {trades}")
					callback(trades)

		except Exception as e:
			logger.error(f"An error occurred while receiving messages: {e}")

	
	def _extract_trades_from_websocket_message(self, msg_json: dict) -> list[Trade]:
		trades = []
		for item in msg_json.get("data"):
			trade = Trade(
				symbol=item.get("symbol").replace("/", ""),
				price=item.get("price"),
				qty=item.get("qty"),
				timestamp_ms= convert_datetime_to_timestamp_in_ms(item.get("timestamp")),
			)
			trades.append(trade)
		return trades


	def subscribe_to_trades(self, symbols: list[str], callback: Callable=None) -> None:
		"""
		Subscribes to trades for the specified symbols and calls the callback with received messages.
		"""
		symbols = [f"{symbol.split('USDT')[0]}/USDT" for symbol in symbols]

		async def run():
			await self.connect()
			msg = {
				"method": "subscribe",
				"params": {
					"channel": "trade",
					"symbol": symbols,
					"snapshot": False,
				},
			}
			await self._ws.send(json.dumps(msg))

			# Set the running flag and start receiving messages
			self._running = True
			await self._receive_messages(callback)

		asyncio.run(run())

	def stop(self):
		"""Stops receiving messages."""
		self._running = False
		if self._ws:
			asyncio.run(self._close())
	
	def close(self):
		self.stop()

	async def _close(self):
		"""Closes the websocket connection."""
		if self._ws:
			await self._ws.close()
			logger.info("WebSocket connection closed.")
