import streamlit as st
import pandas as pd
import plotly.express as px
from dataclasses import asdict

from db_query import get_stats, get_llm_calls

st.set_page_config(
    page_title="Quick Recipes Assistant Dashboard",
    layout="wide"
)

st.title("🍳 Quick Recipes Assistant Dashboard")

stats = get_stats()

limit = st.sidebar.slider(
    "Recent calls",
    min_value=20,
    max_value=1000,
    value=100,
    step=20,
)

records = get_llm_calls(limit=limit)

if not records:
    st.warning("No LLM calls found.")
    st.stop()

df = pd.DataFrame([asdict(r) for r in records])
df["timestamp"] = pd.to_datetime(df["timestamp"])

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Overview",
        "LLM Calls",
        "Evaluation",
        "Feedback"
    ]
)

with tab1:

    st.header("Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total LLM Calls",
        f"{stats.total:,}"
    )

    col2.metric(
        "Avg Response Time",
        f"{stats.avg_response_time:.2f}s"
    )

    col3.metric(
        "Total Cost",
        f"${stats.total_cost:.4f}"
    )

    col4.metric(
        "Avg Tokens",
        f"{stats.avg_tokens:.0f}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Avg Prompt Tokens",
        f"{stats.avg_prompt_tokens:.0f}"
    )

    col2.metric(
        "Avg Completion Tokens",
        f"{stats.avg_completion_tokens:.0f}"
    )

    col3.metric(
        "Total Tokens",
        f"{stats.total_tokens:,}"
    )

    left, right = st.columns(2)

    with left:

        st.subheader("Cost Over Time")

        fig = px.line(
            df.sort_values("timestamp"),
            x="timestamp",
            y="cost",
            markers=True,
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        st.subheader("Response Time")

        fig = px.line(
            df.sort_values("timestamp"),
            x="timestamp",
            y="response_time",
            markers=True,
        )

        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:

        st.subheader("Prompt vs Completion Tokens")

        token_df = pd.DataFrame(
            {
                "Token Type": [
                    "Prompt",
                    "Completion"
                ],
                "Tokens": [
                    stats.avg_prompt_tokens,
                    stats.avg_completion_tokens
                ]
            }
        )

        fig = px.pie(
            token_df,
            names="Token Type",
            values="Tokens",
            hole=0.45,
        )

        fig.update_traces(
            textinfo="label+percent+value"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        st.subheader("Tokens Per Call")

        fig = px.area(
            df.sort_values("timestamp"),
            x="timestamp",
            y=[
                "prompt_tokens",
                "completion_tokens"
            ],
        )

        st.plotly_chart(fig, use_container_width=True)

with tab2:

    st.header("Recent LLM Calls")

    st.dataframe(
        df[
            [
                "timestamp",
                "model",
                "response_time",
                "cost",
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
            ]
        ],
        use_container_width=True,
    )
    idx = st.selectbox(
        "Inspect Call",
        options=df.index.tolist(),
        format_func=lambda i:
            f"{df.loc[i,'timestamp']} | {df.loc[i,'model']}"
    )

    call = df.loc[idx]

    with st.expander("Prompt"):
        st.write(call.prompt)

    with st.expander("Instructions"):
        st.write(call.instructions)

    with st.expander("Answer"):
        st.write(call.answer)

with tab3:

    st.header("Tuning and training")
    st.write('Following metrics are obtained on ground truth data during training:')

    col1, col2, col3 = st.columns(3)

    col1.metric("Hit Rate@5", "92.6%")
    col2.metric("MRR", "0.737")
    col3.metric("LLM Judge", "93.7%")

    evaluation = pd.DataFrame(
        {
            "Metric": [
                "Hit Rate@5",
                "MRR",
                "LLM Judge"
            ],
            "Value": [
                92.6,
                73.7,
                93.7
            ]
        }
    )

    fig = px.bar(
        evaluation,
        x="Metric",
        y="Value",
        text="Value"
    )

    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.write('Following metrics are obtained on live data:')
    st.header("User feedback")