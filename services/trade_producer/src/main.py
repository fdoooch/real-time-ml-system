import logging
import time

from quixstreams import Application

from src.config import config
from src.kraken_api import KrakenWebsocketTradeAPI

logger = logging.getLogger(config.LOGGER_NAME)


def produce_trades(kafka_broker_address: str, kafka_topic: str, symbol: str) -> None:
	"""
	Reads trades from the Kraken websocket API and sends them to a Kafka topic

	Args:
	    kafka_broker_address: The address of the Kafka broker
	    kafka_topic: The name of the Kafka topic
		symbol: The symbol to subscribe to trades for e.g. BTCUSDT
	"""
	logger.debug(f"KAFKA BROKER ADDRESS: {kafka_broker_address}")
	app = Application(kafka_broker_address)

	topic = app.topic(kafka_topic, value_serializer="json")
	kraken_api = KrakenWebsocketTradeAPI(symbol)

	with app.get_producer() as producer:
		while True:
			trades = kraken_api.get_trades()
			for trade in trades:
				message = topic.serialize(key=trade["symbol"], value=trade)

				producer.produce(topic=topic.name, value=message.value, key=message.key)
				logger.debug(f"Produced message: {message}")
				time.sleep(1)


if __name__ == "__main__":
	produce_trades(
		kafka_broker_address=config.kafka.BROKER_ADDRESS,
		kafka_topic=config.kafka.TRADES_TOPIC,
        symbol="BTCUSDT",
	)
