import pandas as pd

class CurrentPriceBaseline:

    def __init__(self):
        ...

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Fitting does nothing
        """
        return None

    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Returns the current price for each symbol
        """
        return X["close"]