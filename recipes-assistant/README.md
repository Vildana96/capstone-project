<h1 align="center"> Quick Recipes Assistant</h1>

<p align="center">
A Retrieval-Augmented Generation (RAG) assistant that recommends quick recipes based on ingredients, cooking time and dietary preferences.
</p>

<p align="center">
<img src="images/istockphoto-1679664848-612x612.jpg" width="600">
</p>

![Python](https://img.shields.io/badge/Python-3.12-blue)

![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.4--mini-green)

![RAG](https://img.shields.io/badge/RAG-Recipe_Assistant-orange)


## Problem  🍳 

Many recipe websites require users to search manually or browse through hundreds of recipes.

This assistant allows users to ask questions such as:

*I have chicken, rice and broccoli. What can I cook in under 30 minutes?
I need a high-protein vegetarian dinner.
I only have 20 minutes and want something healthy.*

Instead of generating recipes from scratch, the assistant retrieves relevant recipes from a curated knowledge base and uses an LLM to produce accurate, context-aware responses.

## Architecture
              
                User Question
                      │
                      ▼
               Index Generation
                      │
                      ▼
             Text Similarity Search
                      │
                      ▼
             Top 5 Relevant Recipes
                      │
                      ▼
              Prompt Construction
                      │
                      ▼
                  LLM Response


## Technologies
  - Python
  - OpenAI API
  - Retrieval-Augmented Generation (RAG)
  - MinSearch
  - PydanticAI
  - Pandas

## Dataset

The assistant uses a curated recipe dataset containing 598 recipes. Each recipe is represented as a structured document with the following fields:
- Recipe name
- Total preparation time
- Number of servings
- Ingredients
- Cooking directions
- Nutritional information (fat, protein, carbohydrates, fiber, vitamins, etc.)


## Project Structure 
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


## Prerequisites
- Python 3.12
- Docker and Docker Compose
- OpenAI API key
- uv for dependency management

## Setup

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

Create a .env file and save key (add to .gitignore)

    OPENAI_API_KEY=your_api_key

Run the assistant

    python app.py


## Ground Truth Generation

Since no labeled retrieval dataset was available, a synthetic ground truth dataset was generated using an LLM.

For every recipe, GPT-5.4-mini generated realistic user search queries designed to retrieve that specific recipe. Instead of simply rewriting recipe titles, the prompt instructed the model to emulate natural user behavior by combining information such as:

- available cooking time
- ingredients on hand
- dietary preferences
- nutritional goals

Example:

    Recipe:
    
    No-Bake Chocolate Coconut Cookies
    Total time: 20 mins
    Servings: 24

    Ingredients:
    - 3 cups quick cooking oats
    ...
    
    Generated query:
    
    Can you give me a quick 20-minute cookie recipe using oats?
    

The generated dataset contains: \
           **598 RECIPES AND 607 QUERIES** \
i.e. 1 expected (ground truth) recipe per query\

Generating the final evaluation dataset cost approximately $0.34 using the OpenAI API. \
I also experimented with generating two synthetic queries per recipe. Although this increased the size of the evaluation dataset, it did not significantly improve retrieval performance while approximately doubling the evaluation cost. Therefore, the final version uses one query per recipe.

## Retrieval Evaluation

Retrieval quality is evaluated using the generated ground truth dataset.


| Metric               | Baseline | Tuned |
| -------------------- | -------- | ----: |
| Hit Rate@5           |   88.0%  | 92.6% |
| MRR                  |   66.1%  | 73.7% |

To improve retrieval quality, different field weights were evaluated on a validation split. The best-performing configuration was:

| Tuned Field |   Recipe name  |  Ingredients  |  Nutrition |
| ------------| -------------- | ------------- | ---------: |
| Weight      |       2        |     5         |    0.5     |

This configuration achieved the best Mean Reciprocal Rank (MRR) before being evaluated on the held-out test set.

## RAG Evaluation

The retrieval component is combined with an LLM to generate grounded recipe recommendations.

For each evaluation query:

- retrieve the Top-5 matching recipes
- generate an answer using the retrieved context
- compare the generated response with the original recipe

Generating responses for all evaluation queries cost approximately $1.26 using the OpenAI API.

## LLM-as-a-Judge Evaluation

The generated answers are automatically evaluated using GPT-5.4-mini acting as an independent judge.

The judge compares:

- the user's question
- the original recipe (ground truth)
- the assistant's generated answer

and labels each response as good or bad based on whether it correctly fulfills the user's request.

| LLM Judge Results    |   Good   |  Bad  |
| -------------------- | -------- | ----: |
| Score Percentage     |   93.7%  |  6.3% |

The LLM judge evaluation cost approximately $0.56.

## Monitoring

To better understand the assistant's behavior and support continuous improvement, every interaction is logged together with LLM usage statistics and evaluation results.

For each user request, the application records metadata such as the model used, prompt and completion token counts, response time, API cost, and timestamp. In addition to operational metrics, the system collects user feedback (👍 / 👎) and LLM-as-a-Judge evaluations, making it possible to analyze both system performance and response quality over time.

A dedicated Streamlit monitoring dashboard visualizes these metrics, helping identify trends in latency, token usage, costs, and feedback while providing detailed inspection of individual interactions.

    User
       │
       ▼
    Quick Recipes Assistant
       │
       ├──────────────► PostgreSQL
       │                 │
       │                 ├── LLM call logs
       │                 └── Feedback
       │
       ▼
    Recipe Response
               ▼
       Streamlit Dashboard
     

### 🤖 Assistant Demo

The following demonstration shows the complete user workflow:

* entering a natural language recipe request,
* retrieving relevant recipes using the RAG pipeline,
* generating a grounded response with an LLM,
* logging the interaction for monitoring,
* collecting optional user feedback.

▶️ ![Assistant Demo](images/assistant_demo.gif)

### 📊 Dashboard Demo

The monitoring dashboard is organized into four tabs:

* **Overview** – summarizes key application metrics, including total LLM calls, response latency, token usage, API cost, and interactive visualizations of cost, response time, and token consumption over time.

* **LLM Calls** – displays recently logged interactions together with model information and detailed inspection of prompts, system instructions, and generated responses, enabling analysis and debugging of individual requests.

* **Evaluation** – presents retrieval and generation quality metrics obtained during the development phase, including Hit Rate@5, Mean Reciprocal Rank (MRR), and LLM-as-a-Judge evaluation scores.

* **Feedback** – aggregates both explicit user feedback (👍/👎) and automated LLM-as-a-Judge assessments. The dashboard visualizes feedback statistics, score distributions, trends over time, and allows detailed inspection of individual conversations together with the corresponding evaluation results.

▶️ *Insert screen recording or GIF here*


## Future Improvements
- Semantic search
- Docker deployment
- Grafana dashboard
- Recipe popularity analytics


