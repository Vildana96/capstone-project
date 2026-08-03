from dataclasses import dataclass

from db_init import get_db_connection
from metrics import LLMCallRecord, Stats, FeedbackRecord, FeedbackStats


def row_to_record(row):
    return LLMCallRecord(
        model=row[3],
        prompt=row[5],
        instructions=row[4],
        answer=row[2],
        prompt_tokens=row[6],
        completion_tokens=row[7],
        total_tokens=row[8],
        response_time=row[9],
        cost=row[10],
        timestamp=row[11],
    )

def feedback_row_to_record(row):
    return FeedbackRecord(
        llm_call_id=row[0],
        query=row[1],
        answer=row[2],
        source=row[3],
        relevance=row[4],
        explanation=row[5],
        score=row[6],
        timestamp=row[7],
    )

def get_llm_calls(limit=10):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, query, answer, model,
                       instructions, prompt,
                       prompt_tokens, completion_tokens, total_tokens,
                       response_time, cost, timestamp
                FROM llm_call_records
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return [row_to_record(row) for row in rows]

def get_stats():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*) AS total,
                    AVG(response_time) AS avg_response_time,
                    SUM(cost) AS total_cost,
                    AVG(total_tokens) AS avg_tokens,
                    AVG(prompt_tokens) AS avg_prompt_tokens,
                    AVG(completion_tokens) AS avg_completion_tokens,
                    SUM(total_tokens) AS total_tokens
                FROM llm_call_records
            """)
            row = cur.fetchone()
    finally:
        conn.close()

    return Stats(
        total=row[0],
        avg_response_time=row[1],
        total_cost=row[2],
        avg_tokens=row[3],
        avg_prompt_tokens=row[4],
        avg_completion_tokens=row[5],
        total_tokens=row[6],

    )

def get_feedback(limit=100):
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    f.llm_call_id,
                    l.query,
                    l.answer,
                    f.source,
                    f.relevance,
                    f.explanation,
                    f.score,
                    f.timestamp
                FROM feedback f
                JOIN llm_call_records l
                    ON f.llm_call_id = l.id
                ORDER BY f.timestamp DESC
                LIMIT %s;
                """,
                (limit,),
            )

            rows = cur.fetchall()

    finally:
        conn.close()

    return [feedback_row_to_record(row) for row in rows]

def get_feedback_stats():
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    COUNT(*) AS total,

                    COUNT(*) FILTER (
                        WHERE source = 'user'
                    ) AS user_total,

                    COUNT(*) FILTER (
                        WHERE source = 'judge'
                    ) AS judge_total,

                    COUNT(*) FILTER (
                        WHERE score = 1 AND source = 'judge') AS judge_positive,
                    COUNT(*) FILTER (
                        WHERE score = 0 AND source = 'judge') AS judge_neutral,
                    COUNT(*) FILTER (
                        WHERE score = -1 AND source = 'judge') AS judge_negative,
                    
                    COUNT(*) FILTER (
                        WHERE score = 1 AND source = 'user') AS user_positive,
                    COUNT(*) FILTER (
                        WHERE score = 0 AND source = 'user') AS user_neutral,
                    COUNT(*) FILTER (
                        WHERE score = -1 AND source = 'user') AS user_negative
                FROM feedback;
                """
            )

            row = cur.fetchone()

    finally:
        conn.close()

    return FeedbackStats(
        total=row[0],
        user_total=row[1],
        judge_total=row[2],
        judge_score_positive=row[3],
        judge_score_negative=row[5],
        judge_score_neutral=row[4],
        user_score_positive=row[6],
        user_score_negative=row[8],
        user_score_neutral=row[7]
    )


if __name__ == "__main__":
    records = get_llm_calls()
    for record in records:
        print(record)