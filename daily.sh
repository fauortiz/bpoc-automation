#!/bin/zsh

# Path to your virtual environment
VENV_PATH="/Users/hipejapaninc./Documents/report-maker/.venv"

# Path to your Python script
SCRIPT_PATH="/Users/hipejapaninc./Documents/report-maker/daily.py"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Run the Python script
exec python "$SCRIPT_PATH" "$@"
