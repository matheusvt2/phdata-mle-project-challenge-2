"""Model loading and prediction service.

Responsible for loading the trained model and demographics data,
augmenting inputs, aligning features, and generating predictions.
"""
import json
import logging
import pickle
from typing import List, Dict, Any, Optional
import pandas as pd
from app.config.settings import get_settings


logger = logging.getLogger(__name__)

class ModelService:
    """Service encapsulating model and feature engineering pipeline."""
    def __init__(self) -> None:
        """Initialize service by loading model, feature order, and demographics."""
        settings = get_settings()

        logger.info("Loading model from %s", settings.model_dir)
        with open(f"{settings.model_dir}/model.pkl", "rb") as f:
            self._model = pickle.load(f)
        with open(f"{settings.model_dir}/model_features.json", "r") as f:
            self._feature_order: List[str] = json.load(f)

        logger.info("Loading demographics from %s",
                   settings.demographics_csv)
        # loads demographics dataset on init
        self._demographics: pd.DataFrame = pd.read_csv(
            settings.demographics_csv, 
            dtype={"zipcode": str}
        )

    def _augment_with_demographics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Join incoming rows with demographics on `zipcode`. Requires zipcode."""
        if "zipcode" not in df.columns:
            raise ValueError("zipcode is required for demographics join")
        df = df.copy()
        merged = df.merge(self._demographics, how="left", on="zipcode")
        # Drop zipcode if not used by the model
        if ("zipcode" not in self._feature_order
                and "zipcode" in merged.columns):
            merged = merged.drop(columns=["zipcode"])
        return merged

    def _to_feature_frame(self, records: List[Dict[float, Any]]) -> pd.DataFrame:
        """Convert list of dicts to a DataFrame aligned to model feature order."""
        raw_df = pd.DataFrame.from_records(records)
        augmented = self._augment_with_demographics(raw_df)

        # Ensure all expected columns present in correct order; add any missing with zeros
        for col in self._feature_order:
            if col not in augmented.columns:
                augmented[col] = 0

        # Remove any extra columns not in the model
        features = augmented[self._feature_order]
        return features

    def predict(self, records: List[Dict[float, Any]]) -> List[float]:
        """Generate predictions for provided records.

        Returns list of floats to be JSON serializable.
        """
        features = self._to_feature_frame(records)
        preds = self._model.predict(features)
        return [float(x) for x in preds]


# Singleton accessor
_singleton: Optional["ModelService"] = None


def get_model_service() -> ModelService:
    """Return a singleton instance of `ModelService`."""
    global _singleton
    if _singleton is None:
        _singleton = ModelService()
    return _singleton
