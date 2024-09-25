import hopsworks
import hsfs
from hsfs.feature_group import FeatureGroup
from dataclasses import dataclass
import pandas as pd


@dataclass
class FeatureGroupOptions:
    name: str
    version: int
    primary_key: list[str]
    event_time: str
    online_enabled: bool = True

@dataclass
class FeatureGroupCreds:
    project_name: str
    api_key: str


def get_or_create_feature_group(
    options: FeatureGroupOptions,
    creds: FeatureGroupCreds,
) -> FeatureGroup:
    conn = hsfs.connection(
        project=creds.project_name,
        api_key_value=creds.api_key,
    )
    
    feature_store = conn.get_feature_store()

    return feature_store.get_or_create_feature_group(
        name=options.name,
        version=options.version,
        primary_key=options.primary_key,
        online_enabled=options.online_enabled,
        # expectation_suite=...
    )
        

def push_feature_to_feature_group(
        feature: dict,
        feature_group: FeatureGroup,
        start_offline_materialization: bool,
) -> None:
    if isinstance(feature, dict):
        if all(isinstance(v, (list, tuple)) for v in feature.values()):
            feature_df = pd.DataFrame(feature)
        else:
            feature_df = pd.DataFrame([feature])
    else:
        raise ValueError("Feature must be a dictionary")
    feature_group.insert(
        features=feature_df,
        write_options={
            "start_offline_materialization": start_offline_materialization,
        },
    )
    print("✔️ Done")


def push_feature_to_feature_store(
        options: FeatureGroupOptions,
        creds: FeatureGroupCreds,
        feature: dict,
        start_offline_materialization: bool,
) -> None:
    project = hopsworks.login(
        project=creds.project_name, 
        api_key_value=creds.api_key,
    )

    feature_store = project.get_feature_store()

    feature_group = feature_store.get_or_create_feature_group(
        name=options.name,
        version=options.version,
        primary_key=options.primary_key,
        online_enabled=options.online_enabled,
        # expectation_suite=...
    )

    if isinstance(feature, dict):
        if all(isinstance(v, (list, tuple)) for v in feature.values()):
            feature_df = pd.DataFrame(feature)
        else:
            feature_df = pd.DataFrame([feature])
    else:
        raise ValueError("Feature must be a dictionary")
    
    feature_group.insert(
        features=feature_df,
        write_options={
            "start_offline_materialization": start_offline_materialization,
        },
    )
    print("✔️ Done")