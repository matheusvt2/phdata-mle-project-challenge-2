"""Prediction API routes.

Exposes endpoints for full and minimal payload predictions. Uses the
`ModelService` to perform data enrichment and inference.
"""
import json
import logging
import pathlib
from datetime import datetime, timezone
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException

from app.api.models.prediction import (
    FullHouseFeatures,
    MinimalHouseFeatures,
    PredictionResponse,
)
from app.services.model_service import get_model_service
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


def save_predictions_to_file(input_records: List[Dict[float, Any]], predictions: List[float], 
                           endpoint_type: str = "full") -> None:
    """Save predictions to model_predictions.json file with input data + predictions."""
    try:
        model_dir = pathlib.Path(settings.model_dir)
        predictions_file = model_dir / "model_predictions.json"
        
        # Load existing predictions if file exists
        existing_predictions = []
        if predictions_file.exists():
            with open(predictions_file, 'r') as f:
                existing_predictions = json.load(f)
        
        # Create new prediction records
        new_predictions = []
        for record, pred in zip(input_records, predictions):
            prediction_record = record.copy()
            prediction_record['price_prediction'] = pred
            prediction_record['price_gt'] = None  # Ground truth price (to be filled manually)
            prediction_record['prediction_timestamp'] = datetime.now(timezone.utc).isoformat()
            prediction_record['endpoint_type'] = endpoint_type
            new_predictions.append(prediction_record)
        
        # Append to existing predictions
        all_predictions = existing_predictions + new_predictions
        
        # Save back to file
        with open(predictions_file, 'w') as f:
            json.dump(all_predictions, f, indent=2)
        
        logger.info("Saved %d predictions to %s", len(new_predictions), predictions_file)
        
    except Exception as exc:
        logger.error("Failed to save predictions: %s", exc)
        # Don't fail the request if saving fails

@router.post("/predict", response_model=List[PredictionResponse])
def predict(items: List[FullHouseFeatures]) -> List[PredictionResponse]:
    """Predict prices for a batch of full feature records.
    """
    try:
        service = get_model_service()
        records: List[Dict[float, Any]] = [i.model_dump() for i in items]
        logger.info("Received %d records for /predict", len(records))
        preds = service.predict(records)
        
        # Save predictions to file
        save_predictions_to_file(records, preds, "full")
        
        model_name = settings.model_name
        now_iso = datetime.now(timezone.utc).isoformat()
        return [
            PredictionResponse(
                prediction=p,
                model=model_name,
                status="success",
                message="Predicted Value in USD",
                datetime=now_iso,
            )
            for p in preds
        ]
    except Exception as exc: 
        logger.exception("Prediction failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/predict/minimal", response_model=List[PredictionResponse])
def predict_minimal(items: List[MinimalHouseFeatures]) -> List[PredictionResponse]:
    """Predict prices for a batch of minimal feature records."""
    try:
        service = get_model_service()
        records: List[Dict[float, Any]] = [i.model_dump() for i in items]
        logger.info("Received %d records for /predict/minimal", len(records))
        preds = service.predict(records)
        
        # Save predictions to file
        save_predictions_to_file(records, preds, "minimal")
        
        model_name = settings.model_name
        now_iso = datetime.now(timezone.utc).isoformat()
        return [
            PredictionResponse(
                prediction=p,
                model=model_name,
                status="success",
                message="Predicted Value in USD",
                datetime=now_iso,
            )
            for p in preds
        ]
    except Exception as exc: 
        logger.exception("Prediction (minimal) failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc