import structlog

# import time
from typing import Dict

from quixstreams import Application

from app.abstract.trades_connector import TradesConnector
from .config import settings
from .trade_producers.bybit_spot_trades_connector import BybitSpotTradesConnector
from .trade_producers.kraken_trades_connector import KrakenTradesConnector

logger = structlog.getLogger(settings.LOGGER_NAME)


class TradesProducer:
	def __init__(self, kafka_broker_address: str, kafka_topic: str) -> None:
		logger.info("Initializing trades producer")
		logger.debug(kafka_broker_address)
		self.kafka_broker_address = kafka_broker_address
		self.kafka = Application(self.kafka_broker_address)
		self.topic = self.kafka.topic(kafka_topic, value_serializer="json")
		self.producer = self.kafka.get_producer()

	def subscribe_to_trades(self, symbols: list[str], source: TradesConnector) -> None:
		source.subscribe_to_trades(symbols, self.push_trade_to_queue)

	def push_trade_to_queue(self, trades: list[Dict]):
		for trade in trades:
			serialized_trade = self.topic.serialize(key=trade.get("symbol"), value=trade)
			self.producer.produce(topic=self.topic.name, value=serialized_trade.value, key=serialized_trade.key)

	def close(self) -> None:
		self.producer.flush()


if __name__ == "__main__":
	# trades_connector: TradesConnector = BybitSpotTradesConnector()
	trades_connector: TradesConnector = KrakenTradesConnector()
	producer = TradesProducer(settings.kafka.BROKER_ADDRESS, settings.kafka.TRADES_TOPIC)
	producer.subscribe_to_trades(["BTCUSDT", "ETHUSDT"], trades_connector)
	try:
		while True:
			...
	except KeyboardInterrupt:...
	finally:
		producer.close()