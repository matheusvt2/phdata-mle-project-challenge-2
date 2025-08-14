"""Quick evaluation utility for the trained model.

Loads the persisted model and evaluates on a held-out split to report
R2 and RMSE. Useful for sanity checks during development.
"""
import json
import pathlib
import pickle
from typing import List

import pandas as pd
from sklearn import metrics, model_selection


DATA_DIR = pathlib.Path("app/data")
MODEL_DIR = pathlib.Path("app/model")


SALES_COLUMN_SELECTION: List[str] = [
    "price",
    "bedrooms",
    "bathrooms",
    "sqft_living",
    "sqft_lot",
    "floors",
    "sqft_above",
    "sqft_basement",
    "zipcode",
]


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load sales and demographics data and return (X, y)."""
    sales_path = DATA_DIR / "kc_house_data.csv"
    demographics_path = DATA_DIR / "zipcode_demographics.csv"
    data = pd.read_csv(sales_path, usecols=SALES_COLUMN_SELECTION, dtype={"zipcode": str})
    demographics = pd.read_csv(demographics_path, dtype={"zipcode": str})
    merged = data.merge(demographics, how="left", on="zipcode").drop(columns="zipcode")
    y = merged.pop("price")
    x = merged
    return x, y


def main() -> None:
    """Compute and print basic generalization metrics for the model."""
    x, y = load_data()
    x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, random_state=42)

    with open(MODEL_DIR / "model.pkl", "rb") as f:
        model = pickle.load(f)
    with open(MODEL_DIR / "model_features.json", "r") as f:
        feature_order = json.load(f)

    # Ensure feature alignment
    for col in feature_order:
        if col not in x_test.columns:
            x_test[col] = 0
    x_test = x_test[feature_order]

    preds = model.predict(x_test)
    r2 = metrics.r2_score(y_test, preds)
    mse = metrics.mean_squared_error(y_test, preds, squared=True)
    rmse = mse ** 0.5

    out = {"mse": mse, "rmse": rmse, "r2": r2}

    # Write production metrics next to the model artifacts
    with open(MODEL_DIR / "metrics_prod.json", "w") as f:
        json.dump(out, f, indent=2)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()


