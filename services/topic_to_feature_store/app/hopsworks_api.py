import hopsworks
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

def push_feature_to_store(
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
        primary_key=options.primary_key,
        online_enabled=options.online_enabled,
        # expectation_suite=...
    )

    print("Pushing feature to store...")

    if isinstance(feature, dict):
        if all(isinstance(v, (list, tuple)) for v in feature.values()):
            feature_df = pd.DataFrame(feature)
        else:
            feature_df = pd.DataFrame([feature])
    else:
        raise ValueError("Feature must be a dictionary")
    breakpoint()
    trans_feature_group.insert(feature_df)
    print("✔️ Done")