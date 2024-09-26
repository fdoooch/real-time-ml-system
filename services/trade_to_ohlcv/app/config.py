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


class KafkaSettings(BaseModel):
	BROKER_ADDRESS: str = os.getenv("KAFKA_BROKER_ADDRESS", "localhost:19092")
	AUTO_OFFSET_RESET: str = os.getenv(
		"KAFKA_AUTO_OFFSET_RESET", "latest"
	)  # earliest, latest, error
	TRADES_TOPIC: str = os.getenv("KAFKA_TRADES_TOPIC", "trade")
	OHLCV_TOPIC: str = os.getenv("KAFKA_OHLCV_TOPIC", "ohlcv")
	CONSUMER_GROUP: str = os.getenv("KAFKA_CONSUMER_GROUP", "trades_to_ohlcv")


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
