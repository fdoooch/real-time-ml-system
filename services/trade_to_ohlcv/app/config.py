import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = os.path.join(BASE_DIR, ".env.trades_to_ohlcv")
load_dotenv(f"{DOTENV_PATH}")
print(f"Loading .env from {DOTENV_PATH}")

def get_kafka_trades_topic_name() -> str:
	env_topic = os.getenv("KAFKA_TRADES_TOPIC")
	if "historical" in env_topic:
		return f"{env_topic}_{os.getenv("BACKFILL_JOB_ID")}"
	return env_topic

def get_kafka_ohlcv_topic_name() -> str:
	env_topic = os.getenv("KAFKA_OHLCV_TOPIC")
	if "historical" in env_topic:
		return f"{env_topic}_{os.getenv("BACKFILL_JOB_ID")}"
	return env_topic

def get_kafka_consumer_group_name() -> str:
	env_group = os.getenv("KAFKA_CONSUMER_GROUP")
	if "historical" in env_group:
		return f"{env_group}_{os.getenv("BACKFILL_JOB_ID")}"
	return env_group



class KafkaSettings(BaseModel):
	BROKER_ADDRESS: str = os.getenv("KAFKA_BROKER_ADDRESS", "localhost:19092")
	AUTO_OFFSET_RESET: str = os.getenv(
		"KAFKA_AUTO_OFFSET_RESET", "latest"
	)  # earliest, latest, error
	TRADES_TOPIC: str = get_kafka_trades_topic_name()
	OHLCV_TOPIC: str = get_kafka_ohlcv_topic_name()
	CONSUMER_GROUP: str = get_kafka_consumer_group_name()


class Settings(BaseSettings):
	PROJECT_NAME: str = "Realtime Trade To OHLCV Aggregator"
	PROJECT_VERSION: str = "0.0.1"
	PROJECT_DESCRIPTION: str = "Aggregate trades to OHLCV and save it to Kafka"
	BASE_DIR: Path = BASE_DIR
	kafka: KafkaSettings = KafkaSettings()
	LOGGER_NAME: str = "trades_to_ohlcv"
	OHLCV_WINDOW_SECONDS: int = os.getenv("OHLCV_WINDOW_SECONDS", 60)


settings = Settings()

logging.basicConfig(
	level=logging.WARNING,
	format="%(asctime)s %(levelname).3s | %(name)s -> %(funcName)s | %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
)
fmt = logging.Formatter(
	fmt="%(asctime)s %(levelname).3s | %(name)s -> %(funcName)s | %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(settings.LOGGER_NAME)
for handler in logger.handlers:
	handler.setFormatter(fmt)
logger.setLevel(logging.DEBUG)
