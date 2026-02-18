import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"


def get_ai_explanation(prompt_text):
    if not API_KEY:
        return "AI disabled. Add GOOGLE_API_KEY in .env"

    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000},
    }

    try:
        r = requests.post(
            f"{GEMINI_API_URL}?key={API_KEY}",
            headers=headers,
            json=payload,
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"AI error: {e}"


def generate_ai_explanation(best_item, purpose, requirements, category):
    specs = best_item.specifications or {}
    category_name = category.name.lower()

    # ---------- category wording ----------
    if "hostel" in category_name or "pg" in category_name:
        thing = "accommodation"
    elif "course" in category_name:
        thing = "course"
    elif "mobile" in category_name:
        thing = "phone"
    else:
        thing = "laptop"

    # ---------- build prompt ----------
    prompt = f"""
You are an expert recommendation assistant.

CATEGORY: {thing}
USER PURPOSE: {purpose}

USER REQUIREMENTS:
Budget: {requirements.get('min_budget')} - {requirements.get('max_budget')}

BEST OPTION:
{best_item.item_name}

SPECIFICATIONS:
{specs}

Explain why this is the best {thing} for the user.
Mention performance, value, and suitability.
If multiple options are similar, explain the trade-offs.
Keep it short (3–4 lines).
"""

    return get_ai_explanation(prompt)
