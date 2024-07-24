from src.kraken_api import KrakenWebsocketTradeAPI

from quixstreams import Application
import time


def produce_trades(
        kafka_broker_address: str,
        kafka_topic: str
) -> None:
    """
    Reads trades from the Kraken websocket API and sends them to a Kafka topic

    Args:
        kafka_broker_address: The address of the Kafka broker
        kafka_topic: The name of the Kafka topic
    """
    app = Application(kafka_broker_address)

    topic = app.topic(kafka_topic, value_serializer='json')
    symbol = "BTCUSDT"
    kraken_api = KrakenWebsocketTradeAPI(symbol)

    with app.get_producer() as producer:
        while True:
            trades = kraken_api.get_trades()
            for trade in trades:
                message = topic.serialize(key=trade["symbol"], value=trade)

                producer.produce(
                    topic=topic.name, value=message.value, key=message.key
                )
                print(f"Produced message: {message}")
                time.sleep(1)



if __name__ == "__main__":
    produce_trades(
        kafka_broker_address="localhost:19092",
        kafka_topic="trade"
    )