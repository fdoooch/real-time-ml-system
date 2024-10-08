import hopsworks
from hsfs.feature_store import FeatureStore
from hsfs.feature_view import FeatureView
from typing import Any
from dataclasses import dataclass
import pandas as pd


@dataclass
class FeatureGroupCreds:
    project_name: str
    api_key: str

@dataclass
class FeatureGroupOptions:
    name: str
    version: int
    primary_key: list[str]
    event_time: str
    creds: FeatureGroupCreds
    online_enabled: bool = True


class OHLCVFeaturesReader:
    def __init__(
        self,
        feature_view: FeatureView,
        ohlcv_window_size_sec: int,
    ):
        self.ohlcv_window_size_sec = ohlcv_window_size_sec
        self.feature_view = feature_view


    def _get_primary_keys_to_read_from_online_store(
            self,
            symbol: str,
            start_time: int,
            end_time: int,
    ) -> list[dict[str, Any]]:
        """
        Returns the primary keys to read from the feature store
        """
        ...

    def read_features_from_offline_store(
            self,
            symbol: str,
            start_time: int,
            end_time: int,
    ) -> pd.DataFrame:
        """
        Reads features from the offline store
        """
        features = self.feature_view.get_batch_data()
        features = features[features["product_id"] == symbol]
        features = features[features["timestamp_ms"] >= start_time]
        features = features[features["timestamp_ms"] <= end_time]
        features = features.sort_values(by="timestamp_ms").reset_index(drop=True)

        return features


    def read(self):
        
        pass



def get_feature_store(hopsworks_creds: FeatureGroupCreds) -> FeatureStore:
    project = hopsworks.login(
        project=hopsworks_creds.project_name,
        api_key_value=hopsworks_creds.api_key,
    )
    return project.get_feature_store()


def get_feature_view(
    fs: FeatureStore,
    feature_view_name: str,
    feature_view_version: int,
) -> FeatureView:
    return fs.get_feature_view(
        name=feature_view_name,
        version=feature_view_version
    )