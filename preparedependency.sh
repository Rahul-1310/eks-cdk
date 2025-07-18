#!/bin/bash
set -e

BASE_DIR="srccode/lambda_dependencies"
PYTHON_DIR="$BASE_DIR/python"

echo "Checking directory structure..."

# Create directories only if they don't exist
if [ ! -d "$PYTHON_DIR" ]; then
    echo "$PYTHON_DIR' does not exist. Creating it."
    mkdir -p "$PYTHON_DIR"
else
    echo "Directory '$PYTHON_DIR' already exists. Skipping creation."
fi

# Install dependencies
echo "Installing/updating Python dependencies into '$PYTHON_DIR'"
pip install -r requirements-lambdalayer.txt -t "$PYTHON_DIR" --upgrade

echo "Dependencies installed successfully."
