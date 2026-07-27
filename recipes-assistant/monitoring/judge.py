import json
from pydantic import BaseModel
from typing import Literal
from openai import OpenAI
from dotenv import load_dotenv
import sys
sys.path.append("..")
from evaluation_utils import llm_structured_retry


class RelevanceVerdict(BaseModel):
    relevance: Literal["NON_RELEVANT", "PARTLY_RELEVANT", "RELEVANT"]
    explanation: str
    usage: float

judge_instructions = """
You are an expert evaluator for a RAG system.
Analyze the relevance of the generated answer to the given question.

Classify the answer as:
- RELEVANT: the answer addresses the question
- PARTLY_RELEVANT: the answer partially addresses the question
- NON_RELEVANT: the answer does not address the question
""".strip()

judge_prompt = """
Query: {query}
Generated Answer: {answer}
""".strip()

def evaluate_relevance(query, answer, client=None):
    if client is None:
        client = OpenAI()

    prompt = judge_prompt.format(
        query=query,
        answer=answer
    )

    result, usage = llm_structured_retry(
        client,
        judge_instructions,
        prompt,
        RelevanceVerdict,
    )

    return result.relevance, result.explanation, result.usage.total_tokens


if __name__ == "__main__":
    load_dotenv()

    query = "I need a high-protein vegetarian dinner."
    answer = "Yes, you can still join. The course is self-paced."

    relevance, explanation = evaluate_relevance(query, answer)
    print(relevance)
    print(explanation)