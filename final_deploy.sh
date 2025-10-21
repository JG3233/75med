#!/bin/bash

# Final deployment script for 75 Hard Challenge app on Raspberry Pi
# Run this only AFTER transferring the updated app.py and config.py

cd ~/75med

# Start the app
echo "🚀 Starting 75 Hard Challenge Tracker..."
echo "Access at: http://$(hostname -I | awk '{print $1}'):5000"
echo "Press Ctrl+C to stop"
echo ""

python3 app.py
