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

for query in query_generator.get_query(q['question']):
    print("trying query: "+query)
    answer = get_answer(query)
    if answer['results']['bindings']:
        q['query'] = query
        q['answer'] = answer


print(build_qald(1, q))