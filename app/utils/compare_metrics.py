"""Compare development vs production metrics.

Reads development metrics from metrics.json and compares with production metrics
calculated from model_predictions.json (when price_gt is available).
"""
import argparse
import json
import numpy as np
from pathlib import Path
from sklearn import metrics


def load_metrics(path: Path) -> dict:
    """Load metrics from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def calculate_production_metrics(predictions_file: str) -> dict:
    """Calculate production metrics from predictions with ground truth."""
    predictions_path = Path(predictions_file)
    if not predictions_path.exists():
        print(f"Warning: Predictions file not found: {predictions_file}")
        return {}
    
    with open(predictions_file, 'r') as f:
        predictions = json.load(f)
    
    # Filter records with both prediction and ground truth
    valid_records = [p for p in predictions if p.get('price_gt') is not None]
    
    if not valid_records:
        print("Warning: No records with ground truth prices found")
        return {}
    
    # Extract predictions and ground truth
    y_pred = [float(p['price_prediction']) for p in valid_records]
    y_true = [float(p['price_gt']) for p in valid_records]
    
    # Calculate metrics (same as in create_model.py)
    mse = metrics.mean_squared_error(y_true, y_pred)
    rmse = mse ** 0.5
    r2 = metrics.r2_score(y_true, y_pred)
    
    return {
        "mse": mse,
        "rmse": rmse, 
        "r2": r2,
        "sample_size": len(valid_records)
    }


def main(dev_file: str, predictions_file: str) -> None:
    """Compare development vs production metrics."""
    
    # Load development metrics
    dev_metrics = load_metrics(Path(dev_file))
    print(f"Development metrics from: {dev_file}")
    print(f"  {json.dumps(dev_metrics, indent=2)}")
    
    # Calculate production metrics from predictions
    prod_metrics = calculate_production_metrics(predictions_file)
    if not prod_metrics:
        print("Could not calculate production metrics")
        return
    
    print(f"\nProduction metrics from: {predictions_file}")
    print(f"  {json.dumps(prod_metrics, indent=2)}")
    
    # Compare metrics
    print("\n" + "="*50)
    print("METRICS COMPARISON")
    print("="*50)
    
    comparison = {}
    for metric in ['mse', 'rmse', 'r2']:
        if metric in dev_metrics and metric in prod_metrics:
            dev_val = float(dev_metrics[metric])
            prod_val = float(prod_metrics[metric])
            delta = prod_val - dev_val
            rel_delta = (delta / dev_val) * 100 if dev_val != 0 else None
            
            comparison[metric] = {
                "development": dev_val,
                "production": prod_val,
                "delta": delta,
                "relative_delta_pct": rel_delta
            }
    
    # Print comparison
    for metric, data in comparison.items():
        print(f"\n{metric.upper()}:")
        print(f"  Development: {data['development']:.6f}")
        print(f"  Production:  {data['production']:.6f}")
        print(f"  Delta:       {data['delta']:+.6f}")
        if data['relative_delta_pct'] is not None:
            print(f"  Change:      {data['relative_delta_pct']:+.2f}%")
    
    # Summary
    print(f"\nSummary:")
    print(f"  Development sample: Test split from training data")
    print(f"  Production sample:  {prod_metrics['sample_size']} predictions with ground truth")


if __name__ == "__main__":
    
    main(dev_file="app/model/metrics.json",predictions_file="app/model/model_predictions.json")


