from .config import settings
from .ohlcv_features_reader import (
    OHLCVFeaturesReader, 
    FeatureGroupCreds,
    get_feature_store,
    get_feature_view,
)
from datetime import datetime as dt

def train_model(
    hopsworks_creds: FeatureGroupCreds,
    symbol: str,
    feature_view_name: str,
    feature_view_version: int,
    ohlcv_window_size_sec: int,
    start_unix_timestamp: int,
    end_unix_timestamp: int,
):
    """
    Reads features from the feature store
    Trains a model
    Saves the model to the model registry
    """

    # Load data from the Feature Store
    fs = get_feature_store(hopsworks_creds)
    feature_view = get_feature_view(fs, feature_view_name, feature_view_version)
    data_reader = OHLCVFeaturesReader(
        feature_view=feature_view,
        ohlcv_window_size_sec=ohlcv_window_size_sec,
    )

    features = data_reader.read_features_from_offline_store(
         symbol=symbol,
         start_time=start_unix_timestamp,
         end_time=end_unix_timestamp
    )
    print(f"Features: {features}")
    # Build the model

    # Push model to the model registry
    ...

def convert_str_to_ms(date_str: str) -> int:
	# Convert
	# "2022-01-01T00:00:00Z"
	# to Unix timestamp in milliseconds
	date = dt.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
	timestamp_ms = int(date.timestamp() * 1000)
	return timestamp_ms


if __name__ == "__main__":

    historical_start_ms = (
		convert_str_to_ms(settings.hopsworks.FEATURE_VIEW_HISTORICAL_SINCE)
		if settings.hopsworks.FEATURE_VIEW_HISTORICAL_SINCE
		else None
	)
    
    historical_end_ms = (
		convert_str_to_ms(settings.hopsworks.FEATURE_VIEW_HISTORICAL_END)
		if settings.hopsworks.FEATURE_VIEW_HISTORICAL_END
		else None
	)
    hopsworks_creds = FeatureGroupCreds(
        api_key=settings.hopsworks.API_KEY,
        project_name=settings.hopsworks.PROJECT_NAME
    )

    train_model(
        hopsworks_creds=hopsworks_creds,
        symbol=settings.SYMBOL,
        feature_view_name=settings.hopsworks.FEATURE_VIEW_NAME,
        feature_view_version=settings.hopsworks.FEATURE_VIEW_VERSION,
        ohlcv_window_size_sec=settings.hopsworks.OHLCV_WINDOW_SIZE_SEC,
        start_unix_timestamp=historical_start_ms,
        end_unix_timestamp=historical_end_ms,
    )