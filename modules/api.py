import requests
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")
API_URL = "http://127.0.0.1:8000"

def add_lead(data):
    return requests.post(f"{API_URL}/leads", json=data)

def analyze_company(data):
    return requests.post(f"{API_URL}/analyze-company", json=data)

def lead_score(data):
    return requests.post(f"{API_URL}/lead-score", json=data)