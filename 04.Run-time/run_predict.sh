#!/bin/bash

# Auto Predict Runtime Runner - Shell Wrapper
# Usage examples:
#   ./run_predict.sh --shape bunny --csv-num 260
#   ./run_predict.sh --batch --shapes bunny squirrel --csv-numbers 260 261
#   ./run_predict.sh --list-shapes

# Change to the directory where this script is located
cd "$(dirname "$0")"

# Check if Python script exists
if [ ! -f "auto_predict_runner.py" ]; then
    echo "Error: auto_predict_runner.py not found in $(pwd)"
    exit 1
fi

# Check if predict-runtime.py exists
if [ ! -f "predict-runtime.py" ]; then
    echo "Error: predict-runtime.py not found in $(pwd)"
    exit 1
fi

# Run the Python script with all arguments passed to this script
python3 auto_predict_runner.py "$@" 