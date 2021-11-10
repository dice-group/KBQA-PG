from get_query import *
from get_answer import *
from gerbil import *

input = "query=What is the capital of Germany?&lang=en"
q = {}

def get_query_lang(input):
    input = input.split('&')
    question = input[0].split('=')[1]
    language = input[1].split('=')[1]
    return question, language

q["question"], q["language"] = get_query_lang(input)

query_generator = QA_query_generation()

for query in query_generator.get_query(q["question"]):
    print("trying query: "+query)
    answer = get_answer(query)
    if answer["results"]["bindings"]:
        q["query"] = query
        answer['head'].pop('link', None)
        answer['results'].pop('distinct', None)
        answer['results'].pop('ordered', None)
        q["answer"] = answer


extract_json(build_qald(1, q))