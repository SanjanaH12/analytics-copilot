import os, requests, json
from dotenv import load_dotenv
load_dotenv(override=True)
from app.baseline import get_schema_text

q = "How many sellers have sold more than 100 order items?"
prompt = f"""You are a PostgreSQL expert. Write ONE read-only PostgreSQL query.
Use only the tables and columns below. Return only SQL, no explanation.

{get_schema_text()}

Question: {q}
SQL:"""
url = f"https://generativelanguage.googleapis.com/v1beta/models/{os.getenv('LLM_MODEL')}:generateContent"
r = requests.post(url, headers={"x-goog-api-key": os.getenv("GEMINI_API_KEY")},
    json={"contents": [{"parts": [{"text": prompt}]}],
          "generationConfig": {"maxOutputTokens": 4000, "temperature": 0}}, timeout=90)
d = r.json()
print("finishReason:", d["candidates"][0].get("finishReason"))
print("usage:", json.dumps(d.get("usageMetadata")))
print("number of parts:", len(d["candidates"][0]["content"]["parts"]))
print("TEXT:\n", d["candidates"][0]["content"]["parts"][0]["text"])