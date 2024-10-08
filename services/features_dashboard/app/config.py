import logging
import os
from pathlib import Path


from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(f"{DOTENV_PATH}")
print(f"Loading .env from {DOTENV_PATH}")


class HopsworksSettings(BaseModel):
    API_KEY: str = os.getenv("HOPSWORKS_API_KEY")
    PROJECT_NAME: str = os.getenv("HOPSWORKS_PROJECT_NAME")
    FEATURE_GROUP_NAME: str = os.getenv("FEATURE_GROUP_NAME")
    FEATURE_GROUP_VERSION: int = int(os.getenv("FEATURE_GROUP_VERSION", 1))
    FEATURE_VIEW_NAME: str = os.getenv("FEATURE_VIEW_NAME")
    FEATURE_VIEW_VERSION: int = int(os.getenv("FEATURE_VIEW_VERSION", 1))


class Settings(BaseSettings):
    PROJECT_NAME: str = "OHLCV Dashboard"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "Visualize OHLCV features from Hopsworks"
    BASE_DIR: Path = BASE_DIR
    hopsworks: HopsworksSettings = HopsworksSettings()
    LOGGER_NAME: str = "ohlcv_dashboard"


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
