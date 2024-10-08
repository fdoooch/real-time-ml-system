from app.config import settings
from app.backend import (
    get_features_from_the_offline_store,
    get_features_from_the_online_store,
)
from app.plot_ohlcv import plot_ohlcv

import pandas as pd
import streamlit as st
# import pandas as pd


def plot_klines(df: pd.DataFrame):
    """
    Plots OHLCV data from a Pandas DataFrame as japanese candlesticks using Bokeh.
    """
    # Create a Bokeh plot

    ...


st.write("""
         # OHLCV features dashboard
         """)

store = st.sidebar.selectbox("Select store", 
    ["kraken_spot", "bybit_spot"]
)
data_type = st.sidebar.selectbox("Select data type", ["online", "historical"])

if data_type == "online":
    data = get_features_from_the_online_store(
            feature_group_name=f"ohlcv_{store}",
            feature_group_version=settings.hopsworks.FEATURE_GROUP_VERSION,
            feature_view_name=settings.hopsworks.FEATURE_VIEW_NAME,
            feature_view_version=settings.hopsworks.FEATURE_VIEW_VERSION,
            hopsworks_project_name=settings.hopsworks.PROJECT_NAME,
            hopsworks_api_key=settings.hopsworks.API_KEY,
        )
    
elif data_type == "offline":
    data = get_features_from_the_offline_store(
            feature_group_name=f"ohlcv_{store}_historical",
            feature_group_version=settings.hopsworks.FEATURE_GROUP_VERSION,
            feature_view_name=settings.hopsworks.FEATURE_VIEW_NAME,
            feature_view_version=settings.hopsworks.FEATURE_VIEW_VERSION,
            hopsworks_project_name=settings.hopsworks.PROJECT_NAME,
            hopsworks_api_key=settings.hopsworks.API_KEY,
        )



st.dataframe(data)

st.bokeh_chart(plot_ohlcv(data))

# df = pd.read_csv("mydata.csv")
# st.line_chart(df)