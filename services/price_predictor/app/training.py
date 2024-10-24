from comet_ml import Experiment
from .config import settings
from .ohlcv_features_reader import (
    OHLCVFeaturesReader,
    FeatureGroupCreds,
    get_feature_store,
    get_feature_view,
)
from app.models import CurrentPriceBaseline, MovingAverageBaseline, XGBoostModel
from app.feature_engineering import add_technical_indicators

from sklearn.metrics import mean_absolute_error
from datetime import datetime as dt
from dataclasses import dataclass
import pandas as pd
import joblib
import logging


logger = logging.getLogger(settings.LOGGER_NAME)


@dataclass
class CometMLCreds:
    api_key: str
    project_name: str


def train_model(
    hopsworks_creds: FeatureGroupCreds,
    comet_ml_creds: CometMLCreds,
    symbol: str,
    feature_view_name: str,
    feature_view_version: int,
    ohlcv_window_size_sec: int,
    start_unix_timestamp: int,
    end_unix_timestamp: int,
    forecast_steps: int,
    num_search_trials: int,
    num_training_data_splits: int,
    num_optimizator_jobs: int,
    percentage_test_data: float = 0.3,
):
    """
    Reads features from the feature store
    Trains a model
    Saves the model to the model registry
    """
    # Create a Comet ML experiment
    experiment = Experiment(
        api_key=comet_ml_creds.api_key, project_name=comet_ml_creds.project_name
    )
    experiment.log_parameters(
        {
            "symbol": symbol,
            "feature_view_name": feature_view_name,
            "feature_view_version": feature_view_version,
            "ohlcv_window_size_sec": ohlcv_window_size_sec,
            "start_unix_timestamp": start_unix_timestamp,
            "end_unix_timestamp": end_unix_timestamp,
            "forecast_steps": forecast_steps,
            "percentage_test_data": percentage_test_data,
            "num_search_trials": num_search_trials,
            "num_training_data_splits": num_training_data_splits,
        }
    )

    # Load data from the Feature Store
    fs = get_feature_store(hopsworks_creds)
    feature_view = get_feature_view(fs, feature_view_name, feature_view_version)
    data_reader = OHLCVFeaturesReader(
        feature_view=feature_view,
        ohlcv_window_size_sec=ohlcv_window_size_sec,
    )

    features = data_reader.read_features_from_offline_store(
        symbol=symbol, start_time=start_unix_timestamp, end_time=end_unix_timestamp
    )
    experiment.log_parameter("num_raw_feature_rows", len(features))

    dataset_hash = pd.util.hash_pandas_object(features).sum()
    experiment.log_parameter("ohlcv_dataset_hash", dataset_hash)

    test_size = int(len(features) * percentage_test_data)
    # Calculate the effective test size, accounting for forecast steps
    effective_test_size = test_size + forecast_steps

    # Split the data, ensuring no overlap
    train_df = features.iloc[:-effective_test_size].copy()
    test_df = features.iloc[-test_size:].copy()

    # Add target column with what we want to predict
    train_df.loc[:, "target_price"] = train_df["close"].shift(-forecast_steps)
    test_df.loc[:, "target_price"] = test_df["close"].shift(-forecast_steps)
    experiment.log_parameters(
        {
            "num_train_feature_rows_before_drop_na": len(train_df),
            "num_test_feature_rows_before_drop_na": len(test_df),
        }
    )
    # Remove rows with NaN targets
    train_df = train_df.dropna()
    test_df = test_df.dropna()
    experiment.log_parameters(
        {
            "num_train_feature_rows_after_drop_na": len(train_df),
            "num_test_feature_rows_after_drop_na": len(test_df),
        }
    )

    # Add technical indicators
    train_df = add_technical_indicators(train_df)
    test_df = add_technical_indicators(test_df)
    train_df = train_df.dropna()
    test_df = test_df.dropna()

    logger.info(f"Train size: {len(train_df)}")
    logger.info(f"Test size: {len(test_df)}")

    # split the data into features (X) and target (y)
    X_train = train_df.drop(columns=["target_price", "product_id"])
    y_train = train_df["target_price"]
    X_test = test_df.drop(columns=["target_price", "product_id"])
    y_test = test_df["target_price"]

    logger.debug(f"X_train columns: {X_train.columns}")
    experiment.log_parameter("features", X_train.columns.to_list())

    # log dimensions of the features and targets
    logger.info(f"X_train shape: {X_train.shape}")
    logger.info(f"y_train shape: {y_train.shape}")
    logger.info(f"X_test shape: {X_test.shape}")
    logger.info(f"y_test shape: {y_test.shape}")
    experiment.log_parameters(
        {
            "X_train_shape": X_train.shape,
            "y_train_shape": y_train.shape,
            "X_test_shape": X_test.shape,
            "y_test_shape": y_test.shape,
        }
    )

    # Build the baseline model'
    model = CurrentPriceBaseline()
    model.fit(X_train, y_train)

    # sanity check
    y_train_pred = model.predict(X_train)
    mae_train = mean_absolute_error(y_train, y_train_pred)
    experiment.log_metric("baseline_mae_train", mae_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    logger.info(f"y_pred shape: {y_pred.shape}")

    # log first 10 predicted values
    logger.info(f"y_pred: {y_pred[:10]}")
    # log first 10 actual values
    logger.info(f"y_test: {y_test[:10]}")

    mae = mean_absolute_error(y_test, y_pred)
    logger.info(f"MAE: {mae}")
    experiment.log_metric("mae_current_price_baseline", mae)

    # train an XGBoost model
    xgb_model = XGBoostModel()
    xgb_model.fit(
        X_train,
        y_train,
        num_search_trials=num_search_trials,
        num_splits=num_training_data_splits,
        num_jobs=num_optimizator_jobs,
    )

    # evaluate the model
    y_pred = xgb_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    logger.info(f"XGB MAE: {mae}")
    experiment.log_metric("mae_xgb_regressor", mae)

    # sanity check
    y_train_pred = xgb_model.predict(X_train)
    mae_train = mean_absolute_error(y_train, y_train_pred)
    experiment.log_metric("xgb_regressor_mae_train", mae_train)

    # Push model to the model registry
    model_name = f"price_predictor_{symbol}_{ohlcv_window_size_sec}_s_{forecast_steps}_steps"
    
    ## Save model locally
    model_path = f"{model_name}.joblib"
    model_path.mkdir(parents=True, exist_ok=True)
    joblib.dump(xgb_model.get_model_object(), model_path)

    experiment.log_model(
        name=model_name,
        
    )


    experiment.end()
    


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
        api_key=settings.hopsworks.API_KEY, project_name=settings.hopsworks.PROJECT_NAME
    )
    comet_ml_creds = CometMLCreds(
        api_key=settings.cometml.API_KEY, project_name=settings.cometml.PROJECT_NAME
    )

    train_model(
        hopsworks_creds=hopsworks_creds,
        comet_ml_creds=comet_ml_creds,
        symbol=settings.SYMBOL,
        feature_view_name=settings.hopsworks.FEATURE_VIEW_NAME,
        feature_view_version=settings.hopsworks.FEATURE_VIEW_VERSION,
        ohlcv_window_size_sec=settings.hopsworks.OHLCV_WINDOW_SIZE_SEC,
        start_unix_timestamp=historical_start_ms,
        end_unix_timestamp=historical_end_ms,
        forecast_steps=settings.FORECAST_STEPS,
        num_search_trials=settings.NUM_SEARCH_TRIALS,
        num_training_data_splits=settings.NUM_TRAINING_DATA_SPLITS,
        num_optimizator_jobs=settings.NUM_OPTIMIZATOR_JOBS,
        percentage_test_data=settings.PERCENTAGE_TEST_DATA,
    )
