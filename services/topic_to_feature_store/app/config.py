import logging
import os
from pathlib import Path


from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = os.path.join(BASE_DIR, ".env.topic_to_feature_store")
load_dotenv(f"{DOTENV_PATH}")
print(f"Loading .env from {DOTENV_PATH}")


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
    INPUT_TOPIC: str = get_kafka_ohlcv_topic_name()
    CONSUMER_GROUP: str = get_kafka_consumer_group_name()
    AUTO_OFFSET_RESET: str = os.getenv("KAFKA_AUTO_OFFSET_RESET", "latest")


class HopsworksSettings(BaseModel):
    API_KEY: str = os.getenv("HOPSWORKS_API_KEY")
    PROJECT_NAME: str = os.getenv("HOPSWORKS_PROJECT_NAME")
    FEATURE_GROUP_NAME: str = os.getenv("FEATURE_GROUP_NAME", "ohlcv")
    FEATURE_GROUP_VERSION: int = int(os.getenv("FEATURE_GROUP_VERSION", 1))
    FEATURE_GROUP_PRIMARY_KEY: list[str] = os.getenv("FEATURE_GROUP_PRIMARY_KEYS", "symbol,timestamp_ms").split(",")
    FEATURE_GROUP_EVENT_TIME: str = os.getenv("FEATURE_GROUP_EVENT_TIME", "timestamp_ms")
    FEATURE_GROUP_ONLINE_ENABLED: bool = os.getenv("FEATURE_GROUP_ONLINE_ENABLED", True)
    PUSHING_BATCH_SIZE: int = int(os.getenv("FEATURE_GROUP_PUSHING_BATCH_SIZE", 1))
    PAUSE_BETWEEN_PUSHING: int = int(os.getenv("FEATURE_GROUP_PAUSE_BETWEEN_PUSHING", 0))
    START_OFFLINE_MATERIALIZATION: bool = os.getenv("FEATURE_GROUP_START_OFFLINE_MATERIALIZATION", False)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Topic to Feature Store Hopsworks"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "Push feature from Kafka to Hopsworks"
    BASE_DIR: Path = BASE_DIR
    kafka: KafkaSettings = KafkaSettings()
    hopsworks: HopsworksSettings = HopsworksSettings()
    LOGGER_NAME: str = "topic_to_feature_store"


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
