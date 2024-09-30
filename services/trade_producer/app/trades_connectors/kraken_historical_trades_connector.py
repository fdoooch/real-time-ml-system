import datetime
import logging
import time
from typing import Callable

import httpx

from app.abstract import TradesConnector
from app.config import settings
from app.schemas.trade_schema import Trade

from .exceptions import (
	TooManyRequestsToTradesSourceError,
)

logger = logging.getLogger(settings.LOGGER_NAME)


def convert_datetime_to_timestamp_in_ms(dt_str: str) -> int:
	dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
	return int(dt.timestamp() * 1000)


class KrakenHistoricalTradesConnector(TradesConnector):
	API_URL = "https://api.kraken.com/0/public/Trades"
	_is_active: bool  # is connector produce any trades or not

	@property
	def is_active(self) -> bool:
		return self._is_active

	def __init__(self):
		self._is_active = False

	def subscribe_to_trades(
		self,
		symbols: list[str],
		callback: Callable = None,
		historical_start_ms: int | None = None,
		historical_end_ms: int | None = None,
	) -> None:
		"""
		Download trades for the specified symbols and calls the callback with received messages.

		        :param symbols: The list of symbols to subscribe to.
		        :param callback: The callback function to be called with the received messages.
		        :param start_unix_epoch_ms: The start timestamp in Unix epoch in milliseconds.
		        :param end_unix_epoch_ms: The end timestamp in Unix epoch in milliseconds.
		"""
		self._is_active = True
		# logger.debug(f"symbols before spliting: {symbols}")
		# symbols = [f"{symbol.split('USDT')[0]}/USDT" for symbol in symbols]
		symbols = [symbol.replace("/", "") for symbol in symbols]

		# logger.debug(f"symbols after spliting: {symbols}")

		for symbol in symbols:
			logger.info(f"Downloading trades for {symbol} from {historical_start_ms} to {historical_end_ms}...")
			self._push_symbol_trades_to_callback(
				symbol=symbol,
				callback=callback,
				start_unix_epoch_ms=historical_start_ms,
				end_unix_epoch_ms=historical_end_ms,
			)
		self._is_active = False
		return None

	def _push_symbol_trades_to_callback(
		self,
		symbol: str,
		callback: Callable,
		start_unix_epoch_ms: int | None,
		end_unix_epoch_ms: int | None,
	) -> None:
		since_ns = start_unix_epoch_ms * 1_000_000 if start_unix_epoch_ms else 0

		if end_unix_epoch_ms:
			end_ns = end_unix_epoch_ms * 1_000_000
		else:
			end_ns = int(datetime.datetime.now().timestamp() * 1000) * 1_000_000

		with httpx.Client() as client:
			while since_ns < end_ns:
				try:
					trades = self._get_trades(
						symbol=symbol,
						since_ns=since_ns,
						end_ns=end_ns,
						http_session=client,
					)
				except TooManyRequestsToTradesSourceError as e:
					logger.warning(e.message)
					time.sleep(30)
					continue
				except Exception as e:
					logger.error(
						f"An error occurred while getting trades: {e} [{type(e)}]"
					)
					breakpoint()
				if trades:
					# print(trades[-1])
					callback(trades)
					since_ns = trades[-1].timestamp_ms * 1_000_000 + 1
					# logger.debug(
					# 	f"since_ns: {since_ns}, end_ns: {end_ns}, last trade: {trades[-1].timestamp_ms}"
					# )
				else:
					break

	def _get_trades(
		self,
		symbol: str,
		since_ns: int,
		end_ns: int,
		http_session: httpx.Client,
	) -> list[Trade]:
		url = f"{self.API_URL}?pair={symbol}&since={since_ns}"
		logger.debug(f"URL: {url}")

		response = http_session.get(url)
		response.raise_for_status()
		data = response.json()

		# logger.debug(data)

		if ("error" in data) and ("EGeneral:Too many requests" in data["error"]):
			raise TooManyRequestsToTradesSourceError(
				"Too many requests to Kraken API trades source."
			)
		if symbol == "BTCUSDT":
			# Krakens symbol for BTCUSDT
			response_symbol = "XBTUSDT"
		else:
			response_symbol = symbol

		trades = [
			Trade(
				symbol=symbol,
				price=trade[0],
				qty=trade[1],
				timestamp_ms=int(trade[2] * 1000),
			)
			for trade in data["result"][response_symbol]
			if (int(trade[2] * 1_000_000_000) < end_ns)
			and (int(trade[2] * 1_000) * 1_000_000 >= since_ns)
		]
		time.sleep(1)
		return trades

	def stop(self): ...

	def close(self):
		self.stop()


def test():
	since_ms = int((
		datetime.datetime.now() - datetime.timedelta(minutes=30)
	).timestamp() * 1000)
	since_ns = since_ms * 1_000_000
	end_ms = int(datetime.datetime.now().timestamp() * 1000)
	end_ns = end_ms * 1_000_000
	symbol = "BTC/USDT"

	print(f"since_ms: {since_ms}")
	print(f"since_ns: {since_ns}")
	print(f"end_ms: {end_ms}")
	print(f"end_ns: {end_ns}")

	with httpx.Client() as client:
		trades = KrakenHistoricalTradesConnector()._get_trades(
			symbol.replace("/", ""), since_ns, end_ns, client
		)
		print(f"trades: {trades}")


if __name__ == "__main__":
	test()
