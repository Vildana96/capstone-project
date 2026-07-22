🍳 Quick Recipes Assistant

A RAG-powered AI assistant that recommends quick recipes based on the ingredients you already have, the time you have available, and your dietary preferences.

The project combines Retrieval-Augmented Generation (RAG), text search, and LLM to provide relevant recipe recommendations instead of relying solely on the model's internal knowledge.

Project status: 🚧 Work in progress

Future work includes adding a production database, analytics dashboard, and deployment.

Problem

Many recipe websites require users to search manually or browse through hundreds of recipes.

This assistant allows users to ask questions such as:

I have chicken, rice and broccoli. What can I cook in under 30 minutes?
I need a high-protein vegetarian dinner.
What's an easy meal with eggs and spinach?
I only have 20 minutes and want something healthy.

Instead of generating recipes from scratch, the assistant retrieves relevant recipes from a curated knowledge base and uses an LLM to produce accurate, context-aware responses.

Architecture
                User Question
                      │
                      ▼
             Embedding Generation
                      │
                      ▼
             Text Similarity Search
                      │
             Top 5 Relevant Recipes
                      │
                      ▼
              Prompt Construction
                      │
                      ▼
                  LLM Response


Technologies
Python
OpenAI API
Retrieval-Augmented Generation (RAG)
Embeddings
MinSearch
PydanticAI
Pandas

Dataset

The assistant uses a curated recipe dataset containing 598 recipes. Each recipe is represented as a structured document with the following fields:

Recipe name
Total preparation time
Number of servings
Ingredients
Cooking directions
Nutritional information (fat, protein, carbohydrates, fiber, vitamins, etc.)


Project Structure (to be updated)
.
├── agent.py              # PydanticAI agent
├── ingest.py             # Dataset loading and indexing
├── evaluate.py           # Retrieval evaluation
├── judge.py              # LLM-as-a-Judge evaluation
├── prompts.py            # Prompt templates
├── app.py                # Assistant entry point
├── data/
├── notebooks/
└── README.md

Prerequisites
Python 3.12
Docker and Docker Compose
OpenAI API key
direnv for environment variables
uv for dependency management

Setup

Clone the repository

git clone https://github.com/Vildana96/capstone-project.git
cd capstone-project

Create a virtual environment

python -m venv .venv

Activate it

Linux / macOS

source .venv/bin/activate

Windows

.venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Create a .env file

OPENAI_API_KEY=your_api_key

Run the assistant

python app.py


Ground Truth Generation

Since no labeled retrieval dataset was available, a synthetic ground truth dataset was generated using an LLM.

For every recipe, GPT-5.4-mini generated realistic user search queries designed to retrieve that specific recipe. Instead of simply rewriting recipe titles, the prompt instructed the model to emulate natural user behavior by combining information such as:

available cooking time
ingredients on hand
dietary preferences
nutritional goals

Example:

Recipe

Persimmon Oatmeal Cookies

Generated query

Can you give me a quick 25-minute cookie recipe using persimmons and oats?

The generated dataset contains:

598 recipes
607 evaluation queries
1 expected (ground truth) recipe per query

Generating the evaluation dataset cost approximately $0.34 using the OpenAI API.


Retrieval Evaluation

Retrieval quality is evaluated using the generated ground truth dataset.

Metrics:

Metric	Baseline	Tuned
Hit Rate@5	0.880	0.926
MRR	0.661	0.737

To improve retrieval quality, different field weights were evaluated on a validation split. The best-performing configuration was:

Field	Weight
Recipe name	2.0
Ingredients	5.0
Nutrition	0.5

This configuration achieved the best Mean Reciprocal Rank (MRR) before being evaluated on the held-out test set.

RAG Evaluation

The retrieval component is combined with an LLM to generate grounded recipe recommendations.

For each evaluation query:

retrieve the Top-5 matching recipes
generate an answer using the retrieved context
compare the generated response with the original recipe

Generating responses for all evaluation queries cost approximately $1.26 using the OpenAI API.

LLM-as-a-Judge Evaluation

The generated answers are automatically evaluated using GPT-5.4-mini acting as an independent judge.

The judge compares:

the user's question
the original recipe (ground truth)
the assistant's generated answer

and labels each response as good or bad based on whether it correctly fulfills the user's request.

Results
Score	Percentage
Good	93.7%
Bad	6.3%

The LLM judge evaluation cost approximately $0.56.

Future Improvements
Semantic search
PostgreSQL + pgvector for vector storage 
Docker deployment
Streamlit frontend
Grafana dashboard
Retrieval monitoring
User feedback collection
Recipe popularity analytics
Continuous evaluation pipeline


Repository

GitHub:

Vildana96/capstone-project