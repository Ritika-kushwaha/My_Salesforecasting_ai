import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GENAI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_company(company_name: str):
    prompt = f"""
You are an AI Sales Intelligence Assistant.

Analyze the company: {company_name}

Return ONLY valid JSON.

{{
    "industry":"",
    "summary":"",
    "sales_opportunity":"",
    "recommended_approach":""
}}

Do not use markdown.
Do not use ```json.
Do not explain anything.
Only return JSON.
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    # Remove markdown if Gemini still returns it
    text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)
def score_lead(company: str, industry: str):
    prompt = f"""
You are an AI Sales Assistant.

Evaluate this sales lead.

Company: {company}
Industry: {industry}

Return ONLY valid JSON.

{{
    "lead_score": 0,
    "priority": "",
    "reason": "",
    "next_action": ""
}}

Rules:
- lead_score should be between 0 and 100.
- priority should be High, Medium, or Low.
- Keep reason short.
- Keep next_action practical.
- Return only JSON.
"""

    response = model.generate_content(prompt)

    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)