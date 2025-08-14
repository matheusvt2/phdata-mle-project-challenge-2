import json
import pathlib
import pickle
import logging
from typing import List
from typing import Tuple

import pandas
from sklearn import model_selection
from sklearn import neighbors
from sklearn import pipeline
from sklearn import preprocessing
from sklearn import metrics

SALES_PATH = "data/kc_house_data.csv"  # path to CSV with home sale data
DEMOGRAPHICS_PATH = "data/zipcode_demographics.csv"  # path to CSV with demographics
# List of columns (subset) that will be taken from home sale data
SALES_COLUMN_SELECTION = [
    'price', 'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'floors',
    'sqft_above', 'sqft_basement', 'zipcode'
]
OUTPUT_DIR = "model"  # Directory where output artifacts will be saved


def load_data(
    sales_path: str, demographics_path: str, sales_column_selection: List[str]
) -> Tuple[pandas.DataFrame, pandas.Series]:
    """Load the target and feature data by merging sales and demographics.

    Args:
        sales_path: path to CSV file with home sale data
        demographics_path: path to CSV file with home sale data
        sales_column_selection: list of columns from sales data to be used as
            features

    Returns:
        Tuple containg with two elements: a DataFrame and a Series of the same
        length.  The DataFrame contains features for machine learning, the
        series contains the target variable (home sale price).

    """
    data = pandas.read_csv(sales_path,
                           usecols=sales_column_selection,
                           dtype={'zipcode': str})
    demographics = pandas.read_csv(demographics_path,
                                   dtype={'zipcode': str})

    merged_data = data.merge(demographics, how="left",
                             on="zipcode").drop(columns="zipcode")
    # Remove the target variable from the dataframe, features will remain
    y = merged_data.pop('price')
    x = merged_data

    return x, y


def main():
    """Load data, train model, and export artifacts."""
    x, y = load_data(SALES_PATH, DEMOGRAPHICS_PATH, SALES_COLUMN_SELECTION)
    x_train, _x_test, y_train, _y_test = model_selection.train_test_split(
        x, y, random_state=42)

    model = pipeline.make_pipeline(preprocessing.RobustScaler(),
                                   neighbors.KNeighborsRegressor()).fit(
                                       x_train, y_train)

    # Evaluate model on held-out test set
    _y_pred = model.predict(_x_test)
    mse = metrics.mean_squared_error(_y_test, _y_pred)
    rmse = mse ** 0.5
    r2 = metrics.r2_score(_y_test, _y_pred)

    output_dir = pathlib.Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    # Persist evaluation metrics
    evaluation_metrics = {"mse": mse, "rmse": rmse, "r2": r2}
    json.dump(evaluation_metrics, open(output_dir / "metrics.json", 'w'), indent=2)
    logging.info("Test metrics: %s", evaluation_metrics)

    # Output model artifacts: pickled model and JSON list of features
    pickle.dump(model, open(output_dir / "model.pkl", 'wb'))
    json.dump(list(x_train.columns),
              open(output_dir / "model_features.json", 'w'))



if __name__ == "__main__":
    main()
