from dataclasses import dataclass

from db_init import get_db_connection
from metrics import LLMCallRecord, Stats


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

def get_relevance_stats():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT relevance, COUNT(*)
                FROM feedback
                WHERE source = 'judge'
                GROUP BY relevance
            """)
            rows = cur.fetchall()
    finally:
        conn.close()
    return dict(rows)

def get_user_feedback_stats():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    SUM(CASE WHEN score > 0 THEN 1 ELSE 0 END),
                    SUM(CASE WHEN score < 0 THEN 1 ELSE 0 END)
                FROM feedback
                WHERE source = 'user'
            """)
            row = cur.fetchone()
    finally:
        conn.close()
    return row


if __name__ == "__main__":
    records = get_llm_calls()
    for record in records:
        print(record)