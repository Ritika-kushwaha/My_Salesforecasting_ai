"""
Top-level entry point for Render deployment.
Imports the FastAPI app from database/main.py as 'server:app'
"""
import sys
import os

# Ensure the repo root is in sys.path so 'database' package resolves
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.main import app  # noqa: F401 - re-exported for uvicorn
