print("starting eval")
import pandas as pd, time
from decimal import Decimal
from app.baseline import get_schema_text, generate_sql
from app.guard import is_safe
from app.executor import run_query
from app.copilot import answer


def norm(v):
    if isinstance(v, (int, float, Decimal)) and not isinstance(v, bool):
        f = float(v)
        return int(f) if f.is_integer() else round(f, 2)
    if hasattr(v, "strftime"):
        return v.strftime("%Y-%m")
    return str(v)


def same_result(gold, pred):
    g = sorted(tuple(norm(x) for x in r) for r in gold)
    p = sorted(tuple(norm(x) for x in r) for r in pred)
    return g == p


schema = get_schema_text()
qs = pd.read_csv("eval/questions.csv")
results = []

for _, row in qs.iterrows():
    status, pred, latency = "fail", "", None
    try:
        t = time.time()
        pred, res, st, retries = answer(row["question"], schema)
        latency = round(time.time() - t, 2)
        if res is None:
            status = st
        else:
            _, gold_rows, _ = run_query(row["gold_sql"])
            same = same_result(gold_rows, res[1])
            status = "pass" if same else "wrong_result"
    except Exception as e:
        status = f"error: {str(e)[:80]}"
    results.append({"question": row["question"], "pred_sql": pred,
                    "status": status, "latency_s": latency})
    print(status, "|", row["question"])
    time.sleep(5)

df = pd.DataFrame(results)
df.to_csv("eval/baseline_results.csv", index=False)
print("Baseline accuracy:", round((df.status == "pass").mean() * 100, 1), "%")