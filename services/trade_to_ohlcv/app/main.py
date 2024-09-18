from quixstreams import Application

async def trade_to_ohlcv(
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
    )
