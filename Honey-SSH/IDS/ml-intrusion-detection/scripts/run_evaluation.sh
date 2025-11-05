#!/bin/bash

# Activate the virtual environment
source ../.venv/bin/activate

# Run the evaluation script
python ../src/evaluation/evaluate.py

# Deactivate the virtual environment
deactivate