import logging
import os
from pathlib import Path


from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(f"{DOTENV_PATH}")


class CometMLSettings(BaseModel):
    API_KEY: str = os.getenv("COMET_ML_API_KEY")
    PROJECT_NAME: str = os.getenv("COMET_ML_PROJECT_NAME")


class HopsworksSettings(BaseModel):
    API_KEY: str = os.getenv("HOPSWORKS_API_KEY")
    PROJECT_NAME: str = os.getenv("HOPSWORKS_PROJECT_NAME")
    FEATURE_VIEW_NAME: str = os.getenv("HOPSWORKS_FEATURE_VIEW_NAME")
    FEATURE_VIEW_VERSION: int = int(os.getenv("HOPSWORKS_FEATURE_VIEW_VERSION", 1))
    FEATURE_VIEW_HISTORICAL_SINCE: str | None = os.getenv("FEATURE_VIEW__HISTORICAL_SINCE")
    FEATURE_VIEW_HISTORICAL_END: str | None = os.getenv("FEATURE_VIEW__HISTORICAL_END")

    FEATURE_GROUP_NAME: str = os.getenv("FEATURE_GROUP_NAME", "ohlcv")
    FEATURE_GROUP_VERSION: int = int(os.getenv("FEATURE_GROUP_VERSION", 1))
    FEATURE_GROUP_PRIMARY_KEY: list[str] = os.getenv("FEATURE_GROUP_PRIMARY_KEYS", "symbol,timestamp_ms").split(",")
    FEATURE_GROUP_EVENT_TIME: str = os.getenv("FEATURE_GROUP_EVENT_TIME", "timestamp_ms")
    FEATURE_GROUP_ONLINE_ENABLED: bool = os.getenv("FEATURE_GROUP_ONLINE_ENABLED", True)
    OHLCV_WINDOW_SIZE_SEC: int = int(os.getenv("OHLCV_WINDOW_SIZE_SEC", 60))
    PUSHING_BATCH_SIZE: int = int(os.getenv("FEATURE_GROUP_PUSHING_BATCH_SIZE", 1))
    PAUSE_BETWEEN_PUSHING: int = int(os.getenv("FEATURE_GROUP_PAUSE_BETWEEN_PUSHING", 0))
    START_OFFLINE_MATERIALIZATION: bool = os.getenv("FEATURE_GROUP_START_OFFLINE_MATERIALIZATION", False)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Price Predictor"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "Push feature from Kafka to Hopsworks"
    BASE_DIR: Path = BASE_DIR
    cometml: CometMLSettings = CometMLSettings()
    hopsworks: HopsworksSettings = HopsworksSettings()
    LOGGER_NAME: str = "price_predictor"
    SYMBOL: str = os.getenv("SYMBOL", "BTCUSDT")
    FORECAST_STEPS: int = int(os.getenv("FORECAST_STEPS", 5))
    NUM_SEARCH_TRIALS: int = int(os.getenv("NUM_SEARCH_TRIALS", 10))
    NUM_TRAINING_DATA_SPLITS: int = int(os.getenv("NUM_TRAINING_DATA_SPLITS", 3))
    NUM_OPTIMIZATOR_JOBS: int = int(os.getenv("NUM_OPTIMIZATOR_JOBS", 1))
    PERCENTAGE_TEST_DATA: float = float(os.getenv("PERCENTAGE_TEST_DATA", 0.3))


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
