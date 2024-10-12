import pandas as pd
import talib as ta

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds technical indicators

    Args:
        df (pd.DataFrame): The dataframe to add technical indicators to.
        Expected columns: open, high, low, close, volume

    Returns:
        pd.DataFrame: The dataframe with the original features and the new technical indicators
    """

    # Add technical indicators
    # Simple Moving Average
    df["sma_7"] = ta.SMA(df["close"], timeperiod=7)
    df["sma_14"] = ta.SMA(df["close"], timeperiod=14)
    df["sma_28"] = ta.SMA(df["close"], timeperiod=28)

    # Exponential Moving Average
    df["ema_7"] = ta.EMA(df["close"], timeperiod=7)
    df["ema_14"] = ta.EMA(df["close"], timeperiod=14)
    df["ema_28"] = ta.EMA(df["close"], timeperiod=28)

    # Moving Average Convergence Divergence (MACD)
    macd, macd_signal, macd_hist = ta.MACD(df["close"], fastperiod=12, slowperiod=26, signalperiod=9)
    df["macd"] = macd
    df["macd_signal"] = macd_signal
    df["macd_hist"] = macd_hist

    # Bollinger Bands
    upper, middle, lower = ta.BBANDS(df["close"], timeperiod=14, nbdevup=2, nbdevdn=2, matype=0)
    df["bb_upper"] = upper
    df["bb_middle"] = middle
    df["bb_lower"] = lower

    # Stochastic Oscillator
    stoch_k, stoch_d = ta.STOCH(df["high"], df["low"], df["close"], fastk_period=14, slowk_period=3, slowd_period=3)
    df["stoch_k"] = stoch_k
    df["stoch_d"] = stoch_d

    # On Balance Volume
    obv = ta.OBV(df["close"], df["volume"])
    df["obv"] = obv

    # Average True Range
    atr = ta.ATR(df["high"], df["low"], df["close"], timeperiod=14)
    df["atr"] = atr

    # Comodity Channel Index (CCI)
    cci = ta.CCI(df["high"], df["low"], df["close"], timeperiod=14)
    df["cci"] = cci

    # Relative Strength Index (RSI)
    rsi = ta.RSI(df["close"], timeperiod=14)
    df["rsi"] = rsi

    # Average Directional Movement Index (ADX)
    adx = ta.ADX(df["high"], df["low"], df["close"], timeperiod=14)
    df["adx"] = adx

    # Chaikin Money Flow (CMF)
    cmf = ta.ADOSC(df["high"], df["low"], df["close"], df["volume"], fastperiod=3, slowperiod=14)
    df["cmf"] = cmf

    return df