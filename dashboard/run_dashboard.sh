#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Ghana ANC Fertility Dashboard — Linux/Unix Launcher
# Run: bash run_dashboard.sh
# ─────────────────────────────────────────────────────────────────────────────

cd "$(dirname "$0")"

echo "=================================================="
echo "  Ghana ANC Fertility Spatial Analysis Dashboard"
echo "=================================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Install with: sudo apt install python3"
    exit 1
fi

# Install dependencies
echo "Checking dependencies..."
python3 -c "import dash, dash_bootstrap_components, plotly, pandas, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install dash dash-bootstrap-components plotly pandas numpy scipy
fi

echo ""
echo "Dashboard starting at http://127.0.0.1:8050"
echo "Press Ctrl+C to stop."
echo ""

# Open browser
sleep 1.5
xdg-open "http://127.0.0.1:8050" 2>/dev/null &

python3 app.py
