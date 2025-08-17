#!/usr/bin/env bash
set -euo pipefail

# ...existing code...
# run_all.sh — execute utility scripts located in app/utils in README order

UTILS_DIR="app/utils"

if [ ! -d "$UTILS_DIR" ]; then
  echo "Utils directory not found: $UTILS_DIR" >&2
  exit 1
fi

echo "Actvating virtualenv..."
source ".venv/bin/activate"
echo "Activated virtualenv: .venv"


echo "Running test_client.py..."
python3 "$UTILS_DIR/test_client.py"


echo "Running docker-cp.sh..."
bash "docker-cp.sh"


echo "Running generate_ground_truth.py..."
python3 "$UTILS_DIR/generate_ground_truth.py"

echo "Running evaluate_model.py..."
python3 "$UTILS_DIR/evaluate_model.py"

echo "Running compare_metrics.py..."
python3 "$UTILS_DIR/compare_metrics.py"

echo "All done."
# ...existing code...