import os, time, requests
from dotenv import load_dotenv
load_dotenv(override=True)

def call_llm(prompt: str, max_tokens: int = 4000) -> str:
    key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("LLM_MODEL")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0},
    }
    last_error = None
    for attempt in range(5):
        try:
            r = requests.post(url, json=body,
                              headers={"x-goog-api-key": key}, timeout=90)
            if r.status_code in (429, 500, 502, 503, 504):
                last_error = f"HTTP {r.status_code}"
                time.sleep(8 * (attempt + 1))
                continue
            r.raise_for_status()
            data = r.json()
            cand = data["candidates"][0]
            if cand.get("finishReason") not in (None, "STOP"):
                last_error = "finishReason=" + str(cand.get("finishReason"))
                time.sleep(3)
                continue
            parts = cand["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
            if text.count("(") != text.count(")"):      # unbalanced brackets = likely cut off
                last_error = "unbalanced brackets"
                time.sleep(3)
                continue
            return text
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as e:
            last_error = type(e).__name__
            time.sleep(8 * (attempt + 1))
    raise RuntimeError(f"LLM call failed after 5 tries: {last_error}")