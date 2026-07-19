from dotenv import load_dotenv
load_dotenv()

from ingest import load_data, build_index
from rag_helper import RAGBase
from openai import OpenAI

documents = load_data()
index = build_index(documents)

openai_client = OpenAI()


def main():
    print("Hello from recipes-assistant!")
    assistant = RAGBase(
    index=index,
    llm_client=openai_client,
)

    answer = assistant.rag("Can you suggest an easy rich in protein recipe?")
    print(answer)


if __name__ == "__main__":
    main()
