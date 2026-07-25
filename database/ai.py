import json
import os
import re
from google import genai

# Load API Key from Environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize Client
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def clean_json_response(text: str) -> dict:
    """Removes markdown code blocks (```json ... ```) and parses string into JSON."""
    cleaned = re.sub(r"```json\s*", "", text)
    cleaned = re.sub(r"```\s*$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return {}


def analyze_company_with_ai(company_name: str, website: str = "", industry: str = "") -> dict:
    """Analyzes a company profile using Gemini 2.5 Flash and returns structured JSON."""
    if not client:
        return {
            "company": company_name,
            "industry": industry if industry else "General Business",
            "lead_score": 75,
            "grade": "B",
            "company_summary": f"{company_name} is an active business operating in the {industry} domain.",
            "sales_opportunity": "Identify primary pain points and cost-optimization goals.",
            "recommended_sales_approach": "Send personalized value-focused introductory email.",
        }

    prompt = f"""
You are an expert enterprise sales intelligence analyst. Analyze this company for B2B sales potential:

Company Name: {company_name}
Website: {website if website else 'Not Provided'}
Industry: {industry if industry else 'General Business'}

Return ONLY a valid JSON object matching this exact key structure:
{{
  "company": "{company_name}",
  "industry": "{industry}",
  "lead_score": 85,
  "grade": "A",
  "company_summary": "Summary of the business background and market focus...",
  "sales_opportunity": "Key expansion opportunities and decision-maker pain points...",
  "recommended_sales_approach": "Recommended outreach strategy..."
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        result = clean_json_response(response.text)
        return result if result else {
            "company": company_name,
            "industry": industry,
            "lead_score": 70,
            "grade": "B",
            "company_summary": f"Research profile generated for {company_name}.",
            "sales_opportunity": "Schedule discovery call to evaluate goals.",
            "recommended_sales_approach": "Direct email campaign.",
        }
    except Exception as e:
        return {
            "company": company_name,
            "industry": industry,
            "lead_score": 65,
            "grade": "C",
            "company_summary": f"Basic research profile for {company_name}.",
            "sales_opportunity": "Explore current tech stack and efficiency needs.",
            "recommended_sales_approach": "Standard outreach.",
            "error": str(e),
        }


def generate_outreach_message(
    name: str, company: str, channel: str = "Cold Email", tone: str = "Professional & Persuasive", value_prop: str = ""
) -> dict:
    """Generates personalized sales outreach copy using Gemini AI."""
    if not client:
        return {
            "subject": f"Quick question regarding {company}",
            "body": f"Hi {name},\n\nI noticed your work at {company}. We help companies streamline their sales process using AI.\n\nWould you be open to a quick call this week?\n\nBest,\nSalesGenie Team",
        }

    prompt = f"""
Write a high-converting {channel} for a B2B sales prospect:

Prospect Name: {name}
Company Name: {company}
Channel: {channel}
Tone: {tone}
Value Proposition: {value_prop if value_prop else 'AI-driven automation to accelerate sales cycles.'}

Return ONLY valid JSON:
{{
  "subject": "Compelling Subject Line",
  "body": "Personalized message body..."
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return clean_json_response(response.text)
    except Exception:
        return {
            "subject": f"Opportunity for {company}",
            "body": f"Hi {name},\n\nWould love to discuss how we can assist {company} in reaching its goals.\n\nBest regards,\nSalesGenie Team",
        }