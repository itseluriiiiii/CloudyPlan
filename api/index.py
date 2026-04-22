import os
import sys

# Bridge to the backend directory
# This allows the Vercel function to find the main.py and services
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app

# Vercel looks for 'app' or 'handler' by default
# Mapping explicitly for clarity
handler = app
