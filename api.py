"""
Top-level entry point for Render deployment.
Wraps database/main.py so uvicorn can find it as 'api:app'
"""
import sys
import os

# Ensure the repo root is in sys.path so 'database' package resolves
sys.path.insert(0, os.path.dirname(__file__))

from database.main import app  # noqa: F401 - re-exported for uvicorn
