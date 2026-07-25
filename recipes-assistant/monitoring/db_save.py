from datetime import datetime
from db_init import get_db_connection, DB_TIMEZONE

def save_llm_call(record, query):
    timestamp = datetime.now(DB_TIMEZONE)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO llm_call_records (
                    query, answer, model, instructions, prompt,
                    prompt_tokens, completion_tokens, total_tokens,
                    response_time, cost, timestamp
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s

                )
                RETURNING id
                """,
                (
                    query,
                    record.answer,
                    record.model,
                    record.instructions,
                    record.prompt,
                    record.prompt_tokens,
                    record.completion_tokens,
                    record.total_tokens,
                    record.response_time,
                    record.cost,
                    timestamp,
                ),
            )
            llm_call_id = cur.fetchone()[0]
            print(f"LLM call saved with ID: {llm_call_id}")
        conn.commit()
    finally:
        conn.close()
    return llm_call_id