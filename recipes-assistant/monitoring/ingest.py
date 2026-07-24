import pandas as pd
from minsearch import Index


def load_data():
    df = pd.read_csv("../data/easy_recipes.csv", dtype=str)
    df.rename(columns={'Unnamed: 0': 'id'}, inplace=True)
    documents = df.to_dict(orient="records")

    return documents


def build_index(documents):
    index = Index(
        text_fields=["recipe_name", "total_time", "servings", "ingredients", "directions", "nutrition"],
    )
    index.fit(documents)
    return index
