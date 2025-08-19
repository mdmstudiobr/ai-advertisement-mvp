import re
import json
import requests
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")
MODEL_NAME = os.getenv("MODEL_NAME", "tinydolphin")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI_API = os.getenv("USE_OPENAI_API", "True").lower() == "true"

# Set OpenAI API key
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


def get_use_openai_api(payload):
    """
    Determines whether to use OpenAI API based on the payload.
    If 'use_openai_api' is not sent, returns True.
    If sent, validates if it's True or False (case-insensitive for string values).
    """
    value = payload.get("use_openai_api", None)
    if value is None:
        return True
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def extract_json(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return {"error": "No JSON object found", "raw": text}
    try:
        return json.loads(match.group(0).replace("\n", "").strip())
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON", "details": str(e), "raw": text}


def generate_ad(make, model, year, km, fuel, transmission, custom_prompt=None, use_openai_api=USE_OPENAI_API):
    # Validate inputs first
    if not all([make, model, year, km, fuel, transmission]):
        return {"error": "Missing required car information", "details": "All fields must be provided"}
    
    # Check if inputs look like valid car data (not random characters)
    if len(make) < 2 or len(model) < 2 or not year.isdigit() or not km.isdigit():
        return {"error": "Invalid car information", "details": "Please provide valid car details"}
    
    prompt = custom_prompt or f"""
Create an engaging car ad for:
- {year} {make} {model}
- {km} km, {fuel}, {transmission}

The advertisement must contain: at least 3 lines and must be something creative, based on real customer reviews, updated (at least 1 year).
Hide the negative aspects, Spotlight the positive aspects.
Search for the prices online for the same model and specs and suggest an average price in US Dollars that could be a good price amount for selling the product.

Use these websites for car sales online as reference if the OpenAIModel is different from the 'tinydolphin':
- https://www.autotrader.com/
- https://www.kbb.com/
- https://www.cars.com/

After creating the advertisement, translate the exact same text to Spanish and also to Brazilian Portuguese.

IMPORTANT: You MUST return ONLY a valid JSON object. If the car information seems invalid or unclear, still try to create a reasonable advertisement based on the provided details.

Return a JSON with:
- field: year, make, model, km, fuel, transmission
- advertisement: english, spanish, brazilian_portuguese
- tags: (comma-separated keywords)
- suggested_reseller_price: $ xxx.xx

Expected JSON output

{{
  "field": {{
    "year": {year},
    "make": "{make}",
    "model": "{model}",
    "km": "{km}",
    "fuel": "{fuel}",
    "transmission": "{transmission}"
  }},
  "advertisement": {{
    "english": "Your English ad text here...",
    "spanish": "Your Spanish ad text here...",
    "brazilian_portuguese": "Your Portuguese ad text here..."
  }},
  "tags": "tag1, tag2, tag3",
  "suggested_reseller_price": "$XX,XXX"
}}

Do not return anything different from the JSON. No additional text or explanations.
"""

    if use_openai_api:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            chat_response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert car seller and translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            response_text = chat_response.choices[0].message.content
            return extract_json(response_text)

        except Exception as e:
            return {"error": "OpenAI request failed", "details": str(e)}

    else:
        try:
            ollama_response = requests.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }, timeout=30)

            if not ollama_response.ok:
                return {"error": "Ollama HTTP error", "status": ollama_response.status_code,
                        "details": ollama_response.text}

            raw_response = ollama_response.json().get("response", "")
            return extract_json(raw_response)

        except Exception as e:
            return {"error": "Ollama request failed", "details": str(e)}