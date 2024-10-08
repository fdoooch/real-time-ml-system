from .config import settings
from .ohlcv_features_reader import (
    OHLCVFeaturesReader, 
    FeatureGroupCreds,
    get_feature_store,
    get_feature_view,
)
from app.models.current_price_baseline import CurrentPriceBaseline

from sklearn.metrics import mean_absolute_error
from datetime import datetime as dt
import logging


logger = logging.getLogger(settings.LOGGER_NAME)

def train_model(
    hopsworks_creds: FeatureGroupCreds,
    symbol: str,
    feature_view_name: str,
    feature_view_version: int,
    ohlcv_window_size_sec: int,
    start_unix_timestamp: int,
    end_unix_timestamp: int,
    forecast_steps: int,
    percentage_test_data: float = 0.3
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

    test_size = int(len(features) * percentage_test_data)
    # Calculate the effective test size, accounting for forecast steps
    effective_test_size = test_size + forecast_steps

    # Split the data, ensuring no overlap
    train_df = features.iloc[:-effective_test_size].copy()
    test_df = features.iloc[-test_size:].copy()

    # Add target column with what we want to predict
    train_df.loc[:, "target_price"] = train_df["close"].shift(-forecast_steps)
    test_df.loc[:, "target_price"] = test_df["close"].shift(-forecast_steps)

    # Remove rows with NaN targets
    train_df = train_df.dropna()
    test_df = test_df.dropna()

    logger.info(f"Train size: {len(train_df)}")
    logger.info(f"Test size: {len(test_df)}")

    # split the data into features (X) and target (y)
    X_train = train_df.drop(columns=["target_price"])
    y_train = train_df["target_price"]
    X_test = test_df.drop(columns=["target_price"])
    y_test = test_df["target_price"]

    # log dimensions of the features and targets
    logger.info(f"X_train shape: {X_train.shape}")
    logger.info(f"y_train shape: {y_train.shape}")
    logger.info(f"X_test shape: {X_test.shape}")
    logger.info(f"y_test shape: {y_test.shape}")
    breakpoint()

    # Build the model'
    model = CurrentPriceBaseline()
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    logger.info(f"y_pred shape: {y_pred.shape}")

    # log first 10 predicted values
    logger.info(f"y_pred: {y_pred[:10]}")
    # log first 10 actual values
    logger.info(f"y_test: {y_test[:10]}") 

    mae = mean_absolute_error(y_test, y_pred)
    logger.info(f"MAE: {mae}")


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
        forecast_steps=settings.FORECAST_STEPS,
        percentage_test_data=settings.PERCENTAGE_TEST_DATA
    )