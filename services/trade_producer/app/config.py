import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from app.enums import TradeSourceName

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(f"{DOTENV_PATH}")
print("JOB_ID: ", os.getenv("BACKFILL_JOB_ID"))

def get_kafka_trades_topic_name() -> str:
	env_topic = os.getenv("KAFKA_TRADES_TOPIC")
	if "historical" in env_topic:
		return f"{env_topic}_{os.getenv('BACKFILL_JOB_ID')}"
	return env_topic


class KafkaSettings(BaseModel):
	BROKER_ADDRESS: str = os.getenv("KAFKA_BROKER_ADDRESS", "localhost:19092")
	TRADES_TOPIC: str = get_kafka_trades_topic_name()


class TradesSourceSettings(BaseModel):
	NAME: TradeSourceName = TradeSourceName(
		os.getenv("TRADES_SOURCE__NAME", "kraken_spot")
	)
	HISTORICAL_SINCE: str | None = os.getenv("TRADES_SOURCE__HISTORICAL_SINCE")
	HISTORICAL_END: str | None = os.getenv("TRADES_SOURCE__HISTORICAL_END")
	SYMBOLS: list[str] = os.getenv("TRADES_SOURCE__SYMBOLS", "").split(",")


class Settings(BaseSettings):
	PROJECT_NAME: str = "Realtime Trade Producer"
	PROJECT_VERSION: str = "0.0.1"
	PROJECT_DESCRIPTION: str = "Produce trade stream to Redpanda"
	BASE_DIR: Path = BASE_DIR
	kafka: KafkaSettings = KafkaSettings()
	LOGGER_NAME: str = "trades_producer"
	trades_source: TradesSourceSettings = TradesSourceSettings()


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
