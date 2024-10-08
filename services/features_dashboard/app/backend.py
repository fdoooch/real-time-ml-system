from .config import settings

import pandas as pd
import hopsworks
from hsfs.feature_view import FeatureView

import time
import logging

logger = logging.getLogger(settings.LOGGER_NAME)


def get_features_from_the_offline_store(
    feature_group_name: str,
    feature_group_version: int,
    feature_view_name: str,
    feature_view_version: int,
    hopsworks_project_name: str,
    hopsworks_api_key: str,
    timestamp_column: str = "timestamp_ms",
) -> pd.DataFrame:
    """
    Fetches features from the store and returns them as a Pandas DataFrame.

    Args:
        feature_group_name (str): The name of the feature group.
        feature_group_version (int): The version of the feature group.
        hopsworks_project_name (str): The name of the Hopsworks project.
        hopsworks_api_key (str): The API key for the Hopsworks project.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the features.
    """
    feature_view = get_feature_view(
        feature_group_name=feature_group_name,
        feature_group_version=feature_group_version,
        feature_view_name=feature_view_name,
        feature_view_version=feature_view_version,
        hopsworks_project_name=hopsworks_project_name,
        hopsworks_api_key=hopsworks_api_key,
    )

    features: pd.DataFrame = feature_view.get_batch_data()

    if timestamp_column not in features.columns:
        raise ValueError(f"Timestamp column '{timestamp_column}' not found in the DataFrame.")
    
    features.sort_values(by=timestamp_column, ascending=True, inplace=True)

    return features


def get_features_from_the_online_store(
    feature_group_name: str,
    feature_group_version: int,
    feature_view_name: str,
    feature_view_version: int,
    hopsworks_project_name: str,
    hopsworks_api_key: str,
    timestamp_column: str = "timestamp_ms",
) -> pd.DataFrame:
    """
    Fetches features from the store and returns them as a Pandas DataFrame.

    Args:
        feature_group_name (str): The name of the feature group.
        feature_group_version (int): The version of the feature group.
        hopsworks_project_name (str): The name of the Hopsworks project.
        hopsworks_api_key (str): The API key for the Hopsworks project.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the features.
    """
    feature_view = get_feature_view(
        feature_group_name=feature_group_name,
        feature_group_version=feature_group_version,
        feature_view_name=feature_view_name,
        feature_view_version=feature_view_version,
        hopsworks_project_name=hopsworks_project_name,
        hopsworks_api_key=hopsworks_api_key,
    )

    features: pd.DataFrame = feature_view.get_feature_vectors(
        entry=_get_the_primary_keys(
            last_n_minutes=60,
            symbol="BTCUSDT",
            timestamp_column=timestamp_column
        ),
        return_type="pandas",
    )

    if timestamp_column not in features.columns:
        raise ValueError(f"Timestamp column '{timestamp_column}' not found in the DataFrame.")
    
    features.sort_values(by=timestamp_column, ascending=True, inplace=True)

    return features


def get_feature_view(
    feature_group_name: str,
    feature_group_version: int,
    feature_view_name: str,
    feature_view_version: int,
    hopsworks_project_name: str,
    hopsworks_api_key: str,
) -> FeatureView:
    
    project = hopsworks.login(
        project=hopsworks_project_name,
        api_key_value=hopsworks_api_key,
    )

    feature_store = project.get_feature_store()

    feature_group = feature_store.get_feature_group(
        name=feature_group_name,
        version=feature_group_version,
    )

    query = feature_group.select_all()

    feature_view = feature_store.get_or_create_feature_view(
        name=feature_view_name,
        version=feature_view_version,
        query=query,
    )

    return feature_view


def _get_the_primary_keys(
        last_n_minutes: int,
        symbol: str,
        timestamp_column: str = "timestamp_ms",
) -> list[dict]:
    now_ms = int(time.time() * 1000)
    now_floored_to_minutes_ms = now_ms - (now_ms % 60000)

    # generate list of timestamps for the last "last_n_minutes" minutes
    timestamps = [now_floored_to_minutes_ms - (i * 60000) for i in range(last_n_minutes)]
    return [
        {
            timestamp_column: timestamp,
            "symbol": symbol
        } for timestamp in timestamps
    ]

    



if __name__ == "__main__":
    data = get_features_from_the_offline_store(
        feature_group_name=settings.hopsworks.FEATURE_GROUP_NAME,
        feature_group_version=settings.hopsworks.FEATURE_GROUP_VERSION,
        feature_view_name=settings.hopsworks.FEATURE_VIEW_NAME,
        feature_view_version=settings.hopsworks.FEATURE_VIEW_VERSION,
        hopsworks_project_name=settings.hopsworks.PROJECT_NAME,
        hopsworks_api_key=settings.hopsworks.API_KEY,
    )
    print(data)