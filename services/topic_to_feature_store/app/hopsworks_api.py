import hopsworks
from dataclasses import dataclass
import pandas as pd


@dataclass
class FeatureGroupOptions:
    name: str
    version: int
    primary_keys: list[str]
    event_time: str
    online_enabled: bool = True

@dataclass
class FeatureGroupCreds:
    project_name: str
    api_key: str

def push_feature_to_to_store(
        feature: dict,
        options: FeatureGroupOptions,
        creds: FeatureGroupCreds,
) -> None:
    project = hopsworks.login(
        project=creds.project_name, 
        api_key_value=creds.api_key,
    )

    feature_store = project .get_feature_store()

    trans_feature_group = feature_store.get_or_create_feature_group(
        name=options.name,
        version=options.version,
        primary_keys=options.primary_keys,
        online_enabled=options.online_enabled,
        # expectation_suite=...
    )


    feature_df = pd.DataFrame.from_dict(feature)
    trans_feature_group.insert(feature_df)
    print("✔️ Done")