INSTRUCTIONS = '''
You are a helpful cooking assistant with extensive knowledge of easy and fast made dishes and their nutritional information. You have access to a database of recipes, including their ingredients, directions, total time, servings, and nutrition facts. Your task is to provide accurate and helpful answers to user questions based on this information.

Your task is to answer questions from the user
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
'''

PROMPT_TEMPLATE = '''
QUESTION: {question}

CONTEXT:
{context}
'''.strip()


class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        model='gpt-5.4-mini'
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.model = model

    def search(self, query, num_results=5):
        boost_dict = {}

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict,
        )

    def build_context(self, search_results):
        entry_template = """
        recipe_name: {recipe_name}, 
        "total_time": {total_time}, 
        "servings": {servings}, 
        "ingredients": {ingredients}, 
        "directions": {directions}, 
        "nutrition": {nutrition}""".strip()

        context = ""

        for doc in search_results:
                context = context + entry_template.format(**doc) + "\n\n"

        return context

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        ).strip()

    def llm(self, prompt):
        input_messages = [
            {'role': 'developer', 'content': self.instructions},
            {'role': 'user', 'content': prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        return response.output_text

    def rag(self, query):
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        answer = self.llm(prompt)
        return answer
