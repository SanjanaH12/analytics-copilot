import os, time, psycopg2
from dotenv import load_dotenv
load_dotenv()

def run_query(sql: str, max_rows: int = 500):
    conn = psycopg2.connect(os.getenv("PG_DSN"))
    try:
        conn.set_session(readonly=True)
        with conn.cursor() as cur:
            cur.execute("SET LOCAL statement_timeout = 5000")
            start = time.time()
            cur.execute(f"SELECT * FROM ({sql.rstrip(';')}) AS t LIMIT {max_rows}")
            cols = [d[0] for d in cur.description]
            return cols, cur.fetchall(), round(time.time() - start, 3)
    finally:
        conn.close()