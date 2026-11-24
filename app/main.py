import csv, os, time
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from app.baseline import get_schema_text
from app.copilot import answer
from collections import defaultdict, deque
from fastapi import Request, HTTPException

HITS = defaultdict(deque)

def rate_limit(ip: str, limit: int = 10, window: int = 60):
    now = time.time()
    q = HITS[ip]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")
    q.append(now)

app = FastAPI(title="Analytics Copilot")
SCHEMA = get_schema_text()
LOG = "logs/queries.csv"
os.makedirs("logs", exist_ok=True)

class Question(BaseModel):
    question: str

def log_row(q, sql, status, retries, latency):
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "question", "sql", "status", "retries", "latency_s"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), q, sql,
                    status, retries, latency])

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/ask")
def ask(body: Question, request: Request):
    rate_limit(request.client.host)
    t = time.time()
    sql, res, status, retries = answer(body.question, SCHEMA)
    latency = round(time.time() - t, 2)
    log_row(body.question, sql, status, retries, latency)
    cols, rows = (res if res else ([], []))
    return {
        "sql": sql, "status": status, "retries": retries, "latency_s": latency,
        "columns": cols,
        "rows": [[str(v) for v in r] for r in rows],
    }