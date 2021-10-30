from get_query import QA_query_generation
from get_answer import get_answer

question = "who is the chancellor of germany?"

query_generator = QA_query_generation()

for query in query_generator.get_query(question):
    get_answer(query)