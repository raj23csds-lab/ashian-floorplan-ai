
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"

URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent"
)


def _generate(prompt):

    if not API_KEY:
        raise RuntimeError("Gemini API key not found in .env file.")

    response = requests.post(
        URL,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        },
        json={
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        },
        timeout=60
    )

    response.raise_for_status()

    result = response.json()

    candidates = result.get("candidates", [])

    if not candidates:
        raise RuntimeError("Gemini returned no response candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])

    text = "".join(
        part.get("text", "") for part in parts
    ).strip()

    if not text:
        raise RuntimeError("Gemini returned an empty response.")

    return text


def generate_sql(question):

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    prompt = """
You are a SQLite query generator for a floor-plan database.

Generate ONE read-only SELECT query for the user's question.

DATABASE SCHEMA:

plans:
- plan_id
- mask
- image

elements:
- id
- plan_id
- source_component_id
- element_type
- class_id
- color
- area_pixels
- x
- y
- width
- height
- centroid_x
- centroid_y

element_links:
- element_id
- room_id
- relation

Allowed element_type values:
room, door, window, wall, opening, furniture

Rules:
1. Use only plans, elements, and element_links.
2. Generate only read-only SELECT statements.
3. Never modify database records.
4. Use only columns present in the supplied schema.
5. Count rooms using element_type = 'room'.
6. For largest room, order by area_pixels DESC LIMIT 1.
7. For rooms without windows, use:
   NOT EXISTS (
       SELECT 1
       FROM element_links AS l
       WHERE l.room_id = r.id
       AND l.relation = 'window_near_room'
   )
8. For average rooms, use AVG(room_count) and ROUND(..., 2).
   Include all plans using LEFT JOIN.
9. For more than N doors, GROUP BY plan_id
   and HAVING COUNT(*) > N.
10. Do not invent tables or columns.
11. If the question cannot be answered from the schema,
    return exactly UNSUPPORTED.
12. Return SQL only. No Markdown fences or explanations.

User question:
""" + question.strip()

    sql = _generate(prompt).strip()

    if sql.startswith("```"):
        sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql


def ask_gemini(prompt):

    try:
        return _generate(prompt)

    except requests.exceptions.RequestException as error:
        return f"Gemini API request failed: {error}"

    except Exception as error:
        return f"Gemini API error: {error}"


if __name__ == "__main__":

    try:
        print(
            ask_gemini(
                "Reply with exactly: Gemini connection successful!"
            )
        )

    except Exception as error:
        print(error)
