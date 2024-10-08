from bokeh.plotting import figure
import pandas as pd
from datetime import timedelta


def plot_ohlcv(
    df: pd.DataFrame,
    window_size_seconds: int | None = 60,
    title: str | None = ""
) -> figure:
    """
    Plots OHLCV data from a Pandas DataFrame as japanese candlesticks using Bokeh.
    """
    df.index = pd.to_datetime(df.index, unit="ms", origin="unix")
    # Create a Bokeh plot
    df["date"] = pd.to_datetime(df.index)
    df["up"] = df["close"] > df["open"]
    df["color"] = df["up"].map({True: "green", False: "red"})

    candles_width = 1000 * window_size_seconds / 2

    TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save"

    x_max = df["date"].max() + timedelta(minutes=5)
    x_min = df["date"].min() - timedelta(minutes=5)
    p = figure(
        x_axis_type="datetime",
        tools=TOOLS,
        width=800, 
        height=300, 
        sizing_mode="stretch_width", 
        x_range=(x_min, x_max),
        title=title
    )
    p.grid.grid_line_alpha = 0.3

    p.segment(df["date"], df["high"], df["date"], df["low"], color="black")
    p.vbar(
        df.date, 
        candles_width, 
        df["open"], 
        df["close"], 
        fill_color="color", 
        line_color="black",
    )
    return p
