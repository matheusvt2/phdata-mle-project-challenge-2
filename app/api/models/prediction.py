"""Pydantic request/response schemas for prediction endpoints.

Defines input feature models and the response payload used by the API.
"""
from typing import Optional
from typing import Optional
from pydantic import BaseModel, Field

class MinimalHouseFeatures(BaseModel):
    """Minimal set of features for the basic model endpoint.

    The service will enrich with demographics and align features before inference.
    """
    bedrooms: int
    bathrooms: float
    sqft_living: int
    sqft_lot: int
    floors: float
    sqft_above: int
    sqft_basement: int
    zipcode: str

class FullHouseFeatures(MinimalHouseFeatures):
    """Complete set of features expected by the baseline model.

    Matches the columns from `future_unseen_examples.csv`.
    """
    waterfront: int
    view: int
    condition: int
    grade: int
    yr_built: int
    yr_renovated: int
    lat: float
    long: float
    sqft_living15: int
    sqft_lot15: int


class PredictionResponse(BaseModel):
    """Prediction payload returned by the API."""
    prediction: float = Field(..., description="Predicted house price")
    model: str = Field("KNeighborsRegressor", description="Model type")
    status: str = Field(..., description="Status of the prediction request (e.g., 'success', 'error')")
    message: Optional[str] = Field(None, description="Additional information or error message")
    datetime: str = Field(..., description="Datetime when the prediction was made (ISO 8601 format)")

