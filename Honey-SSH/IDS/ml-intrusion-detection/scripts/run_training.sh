#!/bin/bash

# Activate the virtual environment
source ../.venv/bin/activate

# Load parameters from the config file
PARAMS_FILE="../configs/params.yaml"
EXPERIMENT_CONFIG="../experiments/config.yaml"

# Run the training script
python ../src/models/train.py --params $PARAMS_FILE --config $EXPERIMENT_CONFIG

# Deactivate the virtual environment
deactivate