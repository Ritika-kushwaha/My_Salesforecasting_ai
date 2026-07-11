from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

# 1. Fetch your key from the environment
api_key = os.getenv("GENAI_API_KEY")
if api_key is None:
    raise ValueError("GENAI_API_KEY is not set in the environment variables.")

# 2. Pass the key to the Google GenAI Client
client = genai.Client(api_key=api_key)

try:
    # 3. Use client.models and a Google model name (like gemini-2.5-flash)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello, world!"
    )
    # 4. Use response.text to print the result
    print("🎉 API connection successful. Response:", response.text)
except Exception as e:
    print("Error occurred while testing API connection:", e)