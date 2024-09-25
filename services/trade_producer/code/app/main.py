import structlog
from app.abstract.trades_connector import TradesConnector
from app.config import settings
from app.enums import TradeSourceName
from app.schemas.trade_schema import Trade
from app.trades_connectors import (
    BybitSpotTradesConnector,
    KrakenHistoricalTradesConnector,
    KrakenTradesConnector,
)
from quixstreams import Application

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
    if settings.TRADES_SOURCE == TradeSourceName.KRAKEN_SPOT:
        settings.kafka.TRADES_TOPIC = "trades_kraken"
        return KrakenTradesConnector()
    elif settings.TRADES_SOURCE == TradeSourceName.KRAKEN_SPOT_HISTORICAL:
        settings.kafka.TRADES_TOPIC = "trades_kraken_historical"
        return KrakenHistoricalTradesConnector()
    elif settings.TRADES_SOURCE == TradeSourceName.BYBIT_SPOT:
        settings.kafka.TRADES_TOPIC = "trades_bybit_spot"
        return BybitSpotTradesConnector()
    raise NotImplementedError


if __name__ == "__main__":
    trades_connector = get_trades_connector()
    producer = TradesProducer(
        settings.kafka.BROKER_ADDRESS, settings.kafka.TRADES_TOPIC
    )
    producer.subscribe_to_trades(["BTCUSDT", "ETHUSDT"], trades_connector)
    try:
        while True:
            ...
    except KeyboardInterrupt:
        ...
    finally:
        producer.close()
