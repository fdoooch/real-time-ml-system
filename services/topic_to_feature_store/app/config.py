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


class KafkaSettings(BaseModel):
    BROKER_ADDRESS: str = os.getenv("KAFKA_BROKER_ADDRESS", "localhost:19092")
    INPUT_TOPIC: str = os.getenv("KAFKA_INPUT_TOPIC", "ohlcv")
    CONSUMER_GROUP: str = os.getenv("KAFKA_CONSUMER_GROUP", "ohlcv_to_feature_store")


class HopsworksSettings(BaseModel):
    USERNAME: str = os.getenv("HOPSWORKS_USERNAME", "admin")
    PASSWORD: str = os.getenv("HOPSWORKS_PASSWORD", "admin")
    API_KEY: str = os.getenv("HOPSWORKS_API_KEY")
    PROJECT_NAME: str = os.getenv("HOPSWORKS_PROJECT_NAME")
    FEATURE_GROUP_NAME: str = os.getenv("FEATURE_GROUP_NAME", "ohlcv")
    FEATURE_GROUP_VERSION: int = int(os.getenv("FEATURE_GROUP_VERSION", 1))
    FEATURE_GROUP_PRIMARY_KEYS: list[str] = os.getenv("FEATURE_GROUP_PRIMARY_KEYS", "symbol,timestamp_ms").split(",")
    FEATURE_GROUP_EVENT_TIME: str = os.getenv("FEATURE_GROUP_EVENT_TIME", "timestamp_ms")
    PUSHING_BATCH_SIZE: int = int(os.getenv("HOPSWORKS_PUSHING_BATCH_SIZE", 10))
    START_OFFLINE_MATERIALIZATION: bool = os.getenv("HOPSWORKS_START_OFFLINE_MATERIALIZATION", False)

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
