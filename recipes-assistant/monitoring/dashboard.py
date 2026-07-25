import streamlit as st
from dataclasses import asdict
import pandas as pd
from db_query import get_llm_calls, get_stats
# get_relevance_stats, get_user_feedback_stats


st.title("Quick Recipes Assistant Dashboard")

stats = get_stats()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total llm call records", stats.total)
col2.metric("Average response time", f"{stats.avg_response_time:.2f}s")
col3.metric("Total cost", f"${stats.total_cost:.4f}")
col4.metric("Average tokens", f"{stats.avg_tokens:.0f}")

records = get_llm_calls(limit=100)
df = pd.DataFrame([asdict(r) for r in records])

st.subheader("Cost over time")
st.line_chart(df, x="timestamp", y="cost")

st.subheader("Response time over time")
st.line_chart(df, x="timestamp", y="response_time")

# st.subheader("Judge relevance")
# relevance = get_relevance_stats()
# st.bar_chart(relevance)

# st.subheader("User feedback")
# thumbs_up, thumbs_down = get_user_feedback_stats()
# col1, col2 = st.columns(2)
# col1.metric("Thumbs up", int(thumbs_up or 0))
# col2.metric("Thumbs down", int(thumbs_down or 0))