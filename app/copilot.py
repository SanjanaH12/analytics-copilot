from app.baseline import generate_sql
from app.llm import call_llm
from app.guard import is_safe
from app.executor import run_query

def _clean(raw: str) -> str:
    return raw.replace("```sql", "").replace("```", "").strip()

def answer(question: str, schema: str, max_retries: int = 2):
    """Returns (sql, (cols, rows) or None, status, retries_used)."""
    sql = generate_sql(question, schema)
    for attempt in range(max_retries + 1):
        if not is_safe(sql):
            return sql, None, "blocked", attempt
        try:
            cols, rows, _ = run_query(sql)
            return sql, (cols, rows), "ok", attempt
        except Exception as e:
            if attempt == max_retries:
                return sql, None, f"error: {str(e)[:80]}", attempt
            prompt = f"""The PostgreSQL query below failed. Fix it.
Return ONE read-only query only, no explanation.

{schema}

Question: {question}
Failed SQL: {sql}
Error: {str(e)[:300]}
Fixed SQL:"""
            sql = _clean(call_llm(prompt))