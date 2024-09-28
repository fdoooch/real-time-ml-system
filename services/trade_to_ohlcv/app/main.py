from datetime import timedelta

import structlog
from quixstreams import Application

from dataclasses import dataclass

from app.config import settings

# TODO: make kline open price as the last price of previous kline


logger = structlog.get_logger(settings.LOGGER_NAME)


@dataclass
class KafkaOptions:
	broker_address: str
	input_topic: str
	output_topic: str | None
	consumer_group: str
	auto_offset_reset: str

def _custom_ts_extractor(
		trade: dict,
		headers: list[tuple[str, bytes]] | None,
		timestamp: float,
		timestamp_type
	) -> int:
	"""
	Specifying a custom timestamp extractor to use the timestamp from trade-messages instead of kafka timestamp
	"""
	return trade["timestamp_ms"]


def trade_to_ohlcv(
	kafka: KafkaOptions,
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
		broker_address=kafka.broker_address,
		consumer_group=kafka.consumer_group,  # In case we have multiple parallel trade-to-ohlcv jobs
		auto_offset_reset=kafka.auto_offset_reset,
	)


	input_topic = app.topic(kafka.input_topic, value_serializer="json", timestamp_extractor=_custom_ts_extractor)
	output_topic = app.topic(kafka.output_topic, value_serializer="json")

	# create a streaming dataframe
	# to apply transformations to data
	sdf = app.dataframe(input_topic)

	# aggregate trades into OHLCV
	sdf = (
		sdf.tumbling_window(duration_ms=timedelta(seconds=ohlcv_window_seconds))
		.reduce(reducer=_update_ohlcv_candle, initializer=_init_ohlcv_candle)
		.final()
	)
	sdf["symbol"] = sdf["value"]["symbol"]
	sdf["open"] = sdf["value"]["open"]
	sdf["high"] = sdf["value"]["high"]
	sdf["low"] = sdf["value"]["low"]
	sdf["close"] = sdf["value"]["close"]
	sdf["volume"] = sdf["value"]["volume"]
	sdf["timestamp_ms"] = sdf["end"]
	sdf = sdf.update(logger.debug)

	sdf = sdf[["symbol", "timestamp_ms", "open", "high", "low", "close", "volume"]]

	# write aggregated trades to Kafka output topic
	sdf.to_topic(output_topic)

	app.run(sdf)


def _init_ohlcv_candle(trade: dict) -> dict:
	"""
	Initialize OHLCV candle with the first trade in the window
	"""
	return {
		"symbol": trade["symbol"],
		"open": trade["price"],
		"high": trade["price"],
		"low": trade["price"],
		"close": trade["price"],
		"volume": trade["qty"],
	}


def _update_ohlcv_candle(kline: dict, trade: dict) -> dict:
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
		"high": max(kline["high"], trade["price"]),
		"low": min(kline["low"], trade["price"]),
		"close": trade["price"],
		"volume": kline["volume"] + trade["qty"],
	}


if __name__ == "__main__":
	logger.info("Starting trade_to_ohlcv")
	kafka_options = KafkaOptions(
		broker_address=settings.kafka.BROKER_ADDRESS,
		input_topic=settings.kafka.TRADES_TOPIC,
		output_topic=settings.kafka.OHLCV_TOPIC,
		consumer_group=settings.kafka.CONSUMER_GROUP,
		auto_offset_reset=settings.kafka.AUTO_OFFSET_RESET,
	)
	trade_to_ohlcv(
		kafka=kafka_options,
		ohlcv_window_seconds=settings.OHLCV_WINDOW_SECONDS,
	)
