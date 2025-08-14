"""Generate synthetic ground truth prices for model predictions.

Adds noise to price predictions to simulate real-world price variations.
Useful for testing model evaluation workflows.
"""
import json
import random
from pathlib import Path
import numpy as np


def add_noise_to_predictions(predictions_file: str, noise_amplitude: float = 100, 
                           random_seed: int = 42) -> None:
    """Add synthetic ground truth prices to predictions with configurable noise."""
    
    # Set random seed for reproducibility
    random.seed(random_seed)
    np.random.seed(random_seed)
    
    # Load existing predictions
    predictions_path = Path(predictions_file)
    if not predictions_path.exists():
        print(f"Error: Predictions file not found: {predictions_file}")
        return
    
    with open(predictions_path, 'r') as f:
        predictions = json.load(f)
    
    print(f"Loaded {len(predictions)} predictions from {predictions_file}")
    
    # Generate ground truth prices (overwrite all)
    updated_count = 0
    for pred_record in predictions:
        # Get the prediction value
        price_pred = pred_record.get('price_prediction')
        if price_pred is None:
            continue
        
        # Generate noise: random between -amplitude and +amplitude
        noise_factor = random.uniform(-noise_amplitude, noise_amplitude)
        
        # Apply noise to prediction
        price_gt = price_pred * (1 + noise_factor)
        
        # Ensure positive price
        price_gt = max(price_gt, price_pred * 0.1)
        
        pred_record['price_gt'] = round(price_gt, 2)
        updated_count += 1
    
    # Save updated predictions
    with open(predictions_path, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f"Updated {updated_count} predictions with ground truth prices")
    print(f"Noise amplitude: ±{noise_amplitude*100:.1f}%")
    print(f"Random seed: {random_seed}")
    
    # Show sample of updated records
    if updated_count > 0:
        print("\nSample updated records:")
        for i, record in enumerate(predictions[:3]):
            if record.get('price_gt') is not None:
                pred = record['price_prediction']
                gt = record['price_gt']
                diff_pct = ((gt - pred) / pred) * 100
                print(f"  Record {i+1}: Pred=${pred:,.0f}, GT=${gt:,.0f} ({diff_pct:+.1f}%)")


if __name__ == "__main__":
     add_noise_to_predictions("app/model/model_predictions.json", 0.2, 42)

