import hopsworks
from hsfs.feature_group import FeatureGroup
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



def get_or_create_feature_group(
    options: FeatureGroupOptions,
) -> FeatureGroup:
    project = hopsworks.login(
        project=options.creds.project_name, 
        api_key_value=options.creds.api_key,
    )
    feature_store = project.get_feature_store()

    print(f"Online Enabled: {options.online_enabled}")

    return feature_store.get_or_create_feature_group(
        name=options.name,
        version=options.version,
        primary_key=options.primary_key,
        event_time=options.event_time,
        online_enabled=options.online_enabled,
        # expectation_suite=...
    )
        

def push_feature_to_feature_group(
        value: list[dict],
        feature_group: FeatureGroup,
        start_offline_materialization: bool,
) -> None:

    value_df = pd.DataFrame(value)
    print(f"Pushing feature to feature group: {feature_group.name}")
    print(f"Online Enabled: {feature_group.online_enabled}")
    print(f"Start offline materialization: {start_offline_materialization}")
    print(f"feature:\n{value_df}")
    i, j = feature_group.insert(
        features=value_df,
        write_options={
            "start_offline_materialization": start_offline_materialization,
            "wait_for_job": False,
            "save_code": False,
        },
    )
    # print("✔️ Done")


# def push_feature_to_feature_store(
#         options: FeatureGroupOptions,
#         creds: FeatureGroupCreds,
#         feature: dict,
#         start_offline_materialization: bool,
# ) -> None:
#     project = hopsworks.login(
#         project=creds.project_name, 
#         api_key_value=creds.api_key,
#     )
#     feature_store = project.get_feature_store()

#     feature_group = feature_store.get_or_create_feature_group(
#         name=options.name,
#         version=options.version,
#         primary_key=options.primary_key,
#         online_enabled=options.online_enabled,
#         # expectation_suite=...
#     )

#     if isinstance(feature, dict):
#         if all(isinstance(v, (list, tuple)) for v in feature.values()):
#             feature_df = pd.DataFrame(feature)
#         else:
#             feature_df = pd.DataFrame([feature])
#     else:
#         raise ValueError("Feature must be a dictionary")
#     feature_group.insert(
#         feature_df,
#         # write_options={
#         #     "start_offline_materialization": start_offline_materialization,
#         # },
#     )
#     print("✔️ Done")