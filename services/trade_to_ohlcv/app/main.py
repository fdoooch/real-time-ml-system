from app.config import settings

from quixstreams import Application
from datetime import timedelta
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
        consumer_group=settings.kafka.GROUP_ID,  # In case we have multiple parallel trade-to-ohlcv jobs
        auto_offset_reset=settings.kafka.AUTO_OFFSET_RESET,
    )
    input_topic = app.topic(kafka_input_topic, value_serializer="json")

    output_topic = app.topic(kafka_output_topic, value_serializer="json")

    # create a streaming dataframe
    # to apply transformations to data
    sdf = app.dataframe(input_topic)

    # aggregate trades into OHLCV
    sdf = (sdf
    .tumbling_window(duration_ms=timedelta(seconds=ohlcv_window_seconds))
    .reduce(reducer=_update_ohlcv_candle, initializer=_init_ohlcv_candle)
    .final()
    )
    sdf['symbol'] = sdf['value']['symbol']
    sdf['open'] = sdf['value']['open']
    sdf['high'] = sdf['value']['high']
    sdf['low'] = sdf['value']['low']
    sdf['close'] = sdf['value']['close']
    sdf['volume'] = sdf['value']['volume']
    sdf['timestamp'] = sdf['start']
    sdf = sdf.update(logger.debug)

    sdf = sdf[['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]

    # write aggregated trades to Kafka output topic
    sdf.to_topic(output_topic)

    app.run(sdf)


def _init_ohlcv_candle(value: dict) -> dict:
    """
    Initialize OHLCV candle with the first trade in the window
    """
    return {
        "symbol": value["symbol"],
        "open": value["price"],
        "high": value["price"],
        "low": value["price"],
        "close": value["price"],
        "volume": value["qty"],
    }

def _update_ohlcv_candle(kline: dict, value: dict) -> dict:
    """
    Update OHLCV candle with the latest trade in the window

    Args:
        kline: dict : Current OHLCV candle
        value: dict : Latest trade

    Returns:
        dict: Updated OHLCV candle
    """
    return {
        "symbol": kline["symbol"],
        "open": kline["open"],
        "high": max(kline["high"], value["price"]),
        "low": min(kline["low"], value["price"]),
        "close": value["price"],
        "volume": kline["volume"] + value["qty"],
    }


if __name__ == "__main__":
    logger.info("Starting trade_to_ohlcv")
    trade_to_ohlcv(
        kafka_input_topic=settings.kafka.TRADES_TOPIC,
        kafka_output_topic=settings.kafka.OHLCV_TOPIC,
        kafka_broker_address=settings.kafka.BROKER_ADDRESS,
        ohlcv_window_seconds=settings.OHLCV_WINDOW_SECONDS,
    )
