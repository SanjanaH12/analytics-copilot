import os, psycopg2
from dotenv import load_dotenv
from app.llm import call_llm
load_dotenv()

def get_schema_text() -> str:
    conn = psycopg2.connect(os.getenv("PG_DSN"))
    cur = conn.cursor()
    cur.execute("""SELECT table_name, column_name, data_type
                   FROM information_schema.columns
                   WHERE table_schema='public'
                   ORDER BY table_name, ordinal_position""")
    tables = {}
    for t, c, d in cur.fetchall():
        tables.setdefault(t, []).append(f"{c} ({d})")
    conn.close()
    schema = "\n".join(f"{t}: {', '.join(cols)}" for t, cols in tables.items())
    notes = open("docs/data_dictionary.md", encoding="utf-8").read()
    rules = open("docs/business_rules.md", encoding="utf-8").read()
    return schema + "\n\nBusiness notes:\n" + notes + "\n\nBusiness rules:\n" + rules

def generate_sql(question: str, schema_text: str) -> str:
    prompt = f"""You are a PostgreSQL expert. Write ONE read-only PostgreSQL query.
Use only the tables and columns below. Return only SQL, no explanation.

{schema_text}

Question: {question}
SQL:"""
    raw = call_llm(prompt)
    return raw.replace("```sql", "").replace("```", "").strip()