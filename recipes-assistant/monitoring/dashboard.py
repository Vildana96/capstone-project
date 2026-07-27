import streamlit as st
from dataclasses import asdict
import pandas as pd
from db_query import get_llm_calls, get_stats
# get_relevance_stats, get_user_feedback_stats
import plotly.express as px


st.title("Quick Recipes Assistant Dashboard")

stats = get_stats()

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "LLM Calls",
    "Evaluation",
    "Search"
])

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("LLM Calls", stats.total)
col2.metric("Avg Response", f"{stats.avg_response_time:.2f}s")
col3.metric("Total Cost", f"${stats.total_cost:.2f}")
col4.metric("Avg Tokens", f"{stats.avg_tokens:.0f}")
col5.metric("Avg Prompt Tokens", f"{stats.avg_prompt_tokens:.0f}")
col6.metric("Avg Completion Tokens", f"{stats.avg_completion_tokens:.0f}")

# col1.metric("Total llm call records", stats.total)
# col2.metric("Average response time", f"{stats.avg_response_time:.2f}s")
# col3.metric("Total cost", f"${stats.total_cost:.4f}")
# col4.metric("Average tokens", f"{stats.avg_tokens:.0f}")

records = get_llm_calls(limit=100)
df = pd.DataFrame([asdict(r) for r in records])

st.subheader("Cost over time")
st.line_chart(df, x="timestamp", y="cost")

st.subheader("Response time over time")
st.line_chart(df, x="timestamp", y="response_time")
st.line_chart(
    df,
    x="timestamp",
    y="total_tokens"
)
st.area_chart(
    df,
    x="timestamp",
    y=["prompt_tokens", "completion_tokens"]
)

st.dataframe(
    df[
        [
            "timestamp",
            "model",
            "response_time",
            "cost",
            "total_tokens"
        ]
    ]
)
selected = st.selectbox(
    "Select LLM Call",
    options=df.index,
)

token_df = pd.DataFrame({
    "Token Type": ["Prompt Tokens", "Completion Tokens"],
    "Tokens": [
        df["prompt_tokens"].sum(),
        df["completion_tokens"].sum(),
    ],
})

fig = px.pie(
    token_df,
    values="Tokens",
    names="Token Type",
    title="Prompt vs Completion Token Distribution",
    hole=0.4,  # donut chart
)

st.plotly_chart(fig, use_container_width=True)

# st.subheader("Judge relevance")
# relevance = get_relevance_stats()
# st.bar_chart(relevance)

# st.subheader("User feedback")
# thumbs_up, thumbs_down = get_user_feedback_stats()
# col1, col2 = st.columns(2)
# col1.metric("Thumbs up", int(thumbs_up or 0))
# col2.metric("Thumbs down", int(thumbs_down or 0))