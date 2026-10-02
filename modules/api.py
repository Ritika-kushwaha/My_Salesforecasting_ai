import requests
import os

try:
    from google import genai as _genai
    _api_key = os.getenv("GEMINI_API_KEY", "")
    _client = _genai.Client(api_key=_api_key) if _api_key else None
except Exception:
    _client = None

API_URL = os.getenv("SALESGENIE_API_URL", "http://127.0.0.1:8000")

def add_lead(data):
    return requests.post(f"{API_URL}/leads", json=data)

def analyze_company(data):
    return requests.post(f"{API_URL}/analyze-company", json=data)

def lead_score(data):
    return requests.post(f"{API_URL}/lead-score", json=data)