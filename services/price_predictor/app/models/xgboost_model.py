from xgboost import XGBRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
import optuna
import pandas as pd
import numpy as np


def _min_mae_objective(
    trial: optuna.trial, X: pd.DataFrame, y: pd.Series, num_splits: int
) -> float:
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_loguniform("learning_rate", 0.01, 0.3),
        "subsample": trial.suggest_loguniform("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_loguniform("colsample_bytree", 0.5, 1.0),
    }

    tscv = TimeSeriesSplit(n_splits=num_splits)

    mae_scores = []
    for train_index, test_index in tscv.split(X):
        X_train, X_valid = X.iloc[train_index], X.iloc[test_index]
        y_train, y_valid = y.iloc[train_index], y.iloc[test_index]

        model = XGBRegressor(**params)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_valid)

        mae = mean_absolute_error(y_valid, y_pred)
        mae_scores.append(mae)
    return np.mean(mae_scores)


def _find_best_hyperparameters(
    X: pd.DataFrame, y: pd.Series, num_search_trials: int, num_splits: int, num_jobs: int
) -> dict:
    study = optuna.create_study(direction="minimize")
    study.optimize(
        lambda trial: _min_mae_objective(trial, X, y, num_splits),
        n_trials=num_search_trials,
        n_jobs=num_jobs,
        show_progress_bar=True,
    )
    return study.best_params


class XGBoostModel:
    _model: XGBRegressor | None

    def __init__(self):
        self._model = None

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        num_search_trials: int | None = 0,
        num_splits: int | None = 3,
        num_jobs: int | None = 1,
    ) -> None:

        assert num_search_trials >= 0, "num search trials must be >= 0"

        if num_search_trials == 0:
            self._model = XGBRegressor()
            self._model.fit(X, y)
            return None

        hyperparams = _find_best_hyperparameters(X, y, num_search_trials, num_splits, num_jobs)
        self._model = XGBRegressor(**hyperparams)
        self._model.fit(X, y)
        return None

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self._model.predict(X)
    

    def get_model_object(self) -> XGBRegressor:
        return self._model
