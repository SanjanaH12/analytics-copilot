import requests
import pandas as pd
import streamlit as st

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Analytics Copilot", layout="wide")
st.title("Analytics Copilot")
st.caption("Ask questions about the Olist e-commerce data in plain English.")

q = st.text_input("Your question", "How many orders were delivered?")

if st.button("Ask") and q.strip():
    with st.spinner("Thinking..."):
        try:
            r = requests.post(f"{API}/ask", json={"question": q}, timeout=180)
            r.raise_for_status()
            d = r.json()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    st.subheader("Generated SQL")
    st.code(d["sql"], language="sql")
    st.write(f"Status: **{d['status']}** | Retries: {d['retries']} | {d['latency_s']} s")

    if d["rows"]:
        df = pd.DataFrame(d["rows"], columns=d["columns"])
        st.dataframe(df, use_container_width=True)
        num = df.apply(pd.to_numeric, errors="coerce")
        numeric_cols = [c for c in num.columns if num[c].notna().all()]
        text_cols = [c for c in df.columns if c not in numeric_cols]
        if len(df) > 1 and numeric_cols and text_cols:
            st.bar_chart(num[numeric_cols[0]].set_axis(df[text_cols[0]]))
    elif d["status"] != "ok":
        st.warning("The query could not be answered. See the status above.")