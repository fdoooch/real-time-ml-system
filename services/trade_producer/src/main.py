import logging

# import time
from typing import Dict

from quixstreams import Application

from src.abstract.trades_connector import TradesConnector
from src.config import config
from src.trade_producers.bybit_spot_trades_connector import BybitSpotTradesConnector

# from src.trade_producers.kraken_trade_connector import KrakenTradeConnector

logger = logging.getLogger(config.LOGGER_NAME)


class TradesProducer:
	def __init__(self, kafka_broker_address: str, kafka_topic: str) -> None:
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
	trades_connector: TradesConnector = BybitSpotTradesConnector()
	producer = TradesProducer(config.kafka.BROKER_ADDRESS, config.kafka.TRADES_TOPIC)
	producer.subscribe_to_trades(["BTCUSDT"], trades_connector)
	try:
		while True:
			...
	except KeyboardInterrupt:...
	finally:
		producer.close()
