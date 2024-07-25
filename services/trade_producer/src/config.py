from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging


BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(f"{DOTENV_PATH}")

class KafkaSettings(BaseModel):
    BROKER_ADDRESS: str = os.getenv('KAFKA_BROKER_ADDRESS', "localhost:19092")
    TRADES_TOPIC: str = os.getenv('KAFKA_TRADES_TOPIC', "trade")


class Settings(BaseSettings):
    PROJECT_NAME: str = "Realtime Trade Producer"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "Produce trade stream to Redpanda"
    BASE_DIR: Path = BASE_DIR
    kafka: KafkaSettings = KafkaSettings()
    LOGGER_NAME: str = "trade_producer"

settings = Settings()

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname).3s | %(name)s -> %(funcName)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
fmt = logging.Formatter(fmt="%(asctime)s %(levelname).3s | %(name)s -> %(funcName)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(settings.LOGGER_NAME)
for handler in logger.handlers:
    handler.setFormatter(fmt)
logger.setLevel(logging.DEBUG)




