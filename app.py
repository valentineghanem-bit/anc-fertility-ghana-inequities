#!/usr/bin/env python3
"""Root-level launcher — delegates to dashboard/app.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dashboard"))
from app import app
server = app.server
if __name__ == "__main__":
    print("Dashboard: http://127.0.0.1:8050")
    app.run(debug=False, host="127.0.0.1", port=8050)
