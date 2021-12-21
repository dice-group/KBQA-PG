from gerbil import *
from get_answer import *
from get_query import *


def load_questions(datafile):
    with open(datafile, "r") as f:
        data = json.load(f)
    return data["questions"]


datafile = r"TEAM1\Data\qald-8-test-multilingual.json"

data = load_questions(datafile)
for question in data:
    question["query"]["sparql"] = ""
    question["answers"][0]["head"]["vars"] = []
    question["answers"][0]["results"]["bindings"] = []

query_generator = QA_query_generation()
for question in data[:2]:
    for query in query_generator.get_query(question["question"][0]["string"]):
        print("trying query: " + query)
        question["query"]["sparql"] = query
        answer = get_answer(query)
        if answer["results"]["bindings"]:
            answer["head"].pop("link", None)
            answer["results"].pop("distinct", None)
            answer["results"].pop("ordered", None)
            question["answers"] = answer
            break

extract_json(data)
