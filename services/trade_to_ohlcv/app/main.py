from app.config import settings

from quixstreams import Application
import structlog


logger = structlog.get_logger(settings.LOGGER_NAME)

def trade_to_ohlcv(
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_broker_address: str,
    ohlcv_window_seconds: int,
) -> None:
    """
    Reads trades from Kafka input_topic,
    aggregates them into OHLCV with specified window size and 
    writes OHLCV to Kafka output topic

    Args:
        kafka_input_topic: Kafka topic to read trades from
        kafka_output_topic: Kafka topic to write OHLCV to
        kafka_broker_address: Kafka broker address
        ohlcv_window_seconds: Window size in seconds to aggregate trades into OHLCV

    Returns:
        None
    """
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=settings.kafka.GROUP_ID, #In case we have multiple parallel trade-to-ohlcv jobs

    )
    input_topic = app.topic(kafka_input_topic, value_serializer='json')

    output_topic = app.topic(kafka_output_topic, value_serializer='json')

    # create a streaming dataframe
    # to apply transformations to data
    sdf = app.dataframe(input_topic)

    # aggregate trades into OHLCV


    # write aggregated trades to Kafka output topic
    sdf.to_topic(output_topic)

    app.run(sdf)


if __name__ == "__main__":
    logger.info("Starting trade_to_ohlcv")
    trade_to_ohlcv(
        kafka_input_topic=settings.kafka.TRADES_TOPIC,
        kafka_output_topic=settings.kafka.OHLCV_TOPIC,
        kafka_broker_address=settings.kafka.BROKER_ADDRESS,
        ohlcv_window_seconds=settings.OHLCV_WINDOW_SECONDS,
    )