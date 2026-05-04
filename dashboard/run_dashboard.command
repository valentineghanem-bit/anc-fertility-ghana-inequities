#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Ghana ANC Fertility Dashboard — macOS Launcher (.command)
# Double-click this file in Finder to launch the dashboard.
# The dashboard will open automatically in your default browser.
# ─────────────────────────────────────────────────────────────────────────────

# Change to the directory containing this script
cd "$(dirname "$0")"

echo "=================================================="
echo "  Ghana ANC Fertility Spatial Analysis Dashboard"
echo "=================================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found."
    echo "Please install Python 3 from https://python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

# Install dependencies if needed
echo "Checking dependencies..."
python3 -c "import dash, dash_bootstrap_components, plotly, pandas, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install dash dash-bootstrap-components plotly pandas numpy scipy --quiet
fi

# Open browser after a short delay
echo "Starting dashboard at http://127.0.0.1:8050"
sleep 1.5
open "http://127.0.0.1:8050" 2>/dev/null || xdg-open "http://127.0.0.1:8050" 2>/dev/null

# Launch app
python3 app.py
