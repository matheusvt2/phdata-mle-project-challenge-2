"""Simple CLI client to call the running API for demonstration/tests."""
import argparse
import json
import pandas as pd
import requests


def batch(n: int, data_path: str, route: str) -> None:
    """Send the first N rows from future_unseen_examples to the API."""
    base_url = f"http://localhost:8000"
    df = pd.read_csv(data_path, dtype={"zipcode": str})
    # loads a batch of n lines
    batch = df.head(n) 
    payload = json.loads(batch.to_json(orient="records"))
    resp = requests.post(f"{base_url}/api/v1/{route}", json=payload, timeout=30)
    print("Status:", resp.status_code)
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    print(f"Response Time (ms): {round(resp.elapsed.total_seconds()*1000,4)}ms")


def inline(n: int, data_path: str, route: str) -> None:
    """Send random N rows from future_unseen_examples to the API sequentially."""
    base_url = f"http://localhost:8000"
    df = pd.read_csv(data_path, dtype={"zipcode": str})
    
    # Select random N rows
    random_rows = df.sample(n=min(n, len(df)), random_state=42)
    
    for i, (idx, row) in enumerate(random_rows.iterrows()):
        payload = json.loads(row.to_frame().T.to_json(orient="records"))
        print(f"\n--- Request {i+1}/{n} (Row {idx}) ---")
        print(f"Data: {payload[0]}")
        
        resp = requests.post(f"{base_url}/api/v1/{route}", json=payload, timeout=30)
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
        print(f"Response Time (ms): {round(resp.elapsed.total_seconds()*1000,4)}ms")


if __name__ == "__main__":
    print("Testing full dataset: Expect SUCCESS")
    batch(n=50,data_path="app/data/future_unseen_examples.csv",route="predict")
    inline(n=5,data_path="app/data/future_unseen_examples.csv",route="predict/minimal")
    print("Testing minimal dataset: Expect HTTPException on route /predict. SUCCESS on /predict/minimal")
    inline(n=1,data_path="app/data/future_unseen_examples_minimal.csv",route="predict")
    batch(n=10,data_path="app/data/future_unseen_examples_minimal.csv",route="predict/minimal")
