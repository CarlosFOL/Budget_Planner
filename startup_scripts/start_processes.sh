#!/bin/bash

# Go to the directory of the project
cd $BP_PATH

# Activate the virtual environment
source venv_bp/bin/activate

# Run the scripts
python3 -m startup_scripts.scripts.season_generator
