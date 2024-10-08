import pandas as pd


class MovingAverageBaseline:
    def __init__(self, window_size: int):
        self.window_size = window_size

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Fitting does nothing
        """
        return None

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError