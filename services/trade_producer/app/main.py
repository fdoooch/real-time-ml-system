from datetime import datetime as dt

import structlog
from quixstreams import Application

from app.abstract.trades_connector import TradesConnector
from app.config import settings
from app.enums import TradeSourceName
from app.schemas.trade_schema import Trade
from app.trades_connectors import (
	BybitSpotTradesConnector,
	KrakenHistoricalTradesConnector,
	KrakenTradesConnector,
)

logger = structlog.getLogger(settings.LOGGER_NAME)





class TradesProducer:
	sources = [TradesConnector]

	@property
	def is_active(self) -> bool:
		for source in self.sources:
			if source.is_active:
				return True
		return False

	def __init__(
		self,
		kafka_broker_address: str,
		kafka_topic: str,
	) -> None:
		logger.info("Initializing trades producer")
		logger.debug(kafka_broker_address)
		self.sources = []
		self.kafka_broker_address = kafka_broker_address
		self.kafka = Application(self.kafka_broker_address)
		self.topic = self.kafka.topic(kafka_topic, value_serializer="json")
		self.producer = self.kafka.get_producer()

	def subscribe_to_trades(
		self,
		symbols: list[str],
		source: TradesConnector,
		historical_start_ms: int | None = None,
		historical_end_ms: int | None = None,
	) -> None:
		self.sources.append(source)
		source.subscribe_to_trades(
			symbols=symbols,
			callback=self.push_trade_to_queue,
			historical_start_ms=historical_start_ms,
			historical_end_ms=historical_end_ms,
		)

	def push_trade_to_queue(self, trades: list[Trade]):
		for trade in trades:
			serialized_trade = self.topic.serialize(
				key=trade.symbol, value=trade.model_dump()
			)
			self.producer.produce(
				topic=self.topic.name,
				value=serialized_trade.value,
				key=serialized_trade.key,
			)
			logger.debug(f"Pushed trade to Kafka: {trade}")

	def close(self) -> None:
		self.producer.flush()


def get_trades_connector() -> TradesConnector:
	if settings.trades_source.NAME == TradeSourceName.KRAKEN_SPOT:
		settings.kafka.TRADES_TOPIC = "trades_kraken_spot"
		return KrakenTradesConnector()
	elif settings.trades_source.NAME == TradeSourceName.KRAKEN_SPOT_HISTORICAL:
		settings.kafka.TRADES_TOPIC = "trades_kraken_spot_historical"
		return KrakenHistoricalTradesConnector()
	elif settings.trades_source.NAME == TradeSourceName.BYBIT_SPOT:
		settings.kafka.TRADES_TOPIC = "trades_bybit_spot"
		return BybitSpotTradesConnector()
	raise NotImplementedError


def convert_str_to_ms(date_str: str) -> int:
	# Convert
	# "2022-01-01T00:00:00Z"
	# to Unix timestamp in milliseconds
	date = dt.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
	timestamp_ms = int(date.timestamp() * 1000)
	return timestamp_ms


if __name__ == "__main__":
	trades_connector = get_trades_connector()
	producer = TradesProducer(
		settings.kafka.BROKER_ADDRESS, settings.kafka.TRADES_TOPIC
	)
	historical_start_ms = (
		convert_str_to_ms(settings.trades_source.HISTORICAL_SINCE)
		if settings.trades_source.HISTORICAL_SINCE
		else None
	)
	historical_end_ms = (
		convert_str_to_ms(settings.trades_source.HISTORICAL_END)
		if settings.trades_source.HISTORICAL_END
		else None
	)
	producer.subscribe_to_trades(
		symbols=settings.trades_source.SYMBOLS,
		source=trades_connector,
		historical_start_ms=historical_start_ms,
		historical_end_ms=historical_end_ms,
	)
	try:
		while producer.is_active:
			...
	except KeyboardInterrupt:
		...
	finally:
		producer.close()
