#!/bin/bash

echo "Starting AuraMotion Studio..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.10+ and try again"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import cv2, mediapipe, numpy, pygame, tkinter, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

# Run the application
echo "Launching AuraMotion Studio..."
python3 auramotion_studio.py

if [ $? -ne 0 ]; then
    echo
    echo "Application closed with an error."
fi
