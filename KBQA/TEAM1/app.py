from gerbil import *
from get_answer import *
from get_query import *

# load questions from dataset
def load_questions(datafile):
    with open(datafile, "r") as f:
        data = json.load(f)
    return data["questions"]


datafile = r"TEAM1\Data\qald-8-test-multilingual.json"

data = load_questions(datafile)

# clean queries and answers for each question from dataset
for question in data:
    question["query"]["sparql"] = ""
    question["answers"][0]["head"]["vars"] = []
    question["answers"][0]["results"]["bindings"] = []

query_generator = QA_query_generation()
for question in data[:5]:
    for quest in question["question"]:
        # only consider English questions
        if quest["language"] == "en":
            # try every query from generator
            for query in query_generator.get_query(quest["string"]):
                print("trying query: " + query)
                question["query"]["sparql"] = query
                answer = get_answer(query)
                if answer["results"]["bindings"]:
                    # delete extra keys
                    answer["head"].pop("link", None)
                    answer["results"].pop("distinct", None)
                    answer["results"].pop("ordered", None)
                    question["answers"] = answer
                    # if we found an answer, go to next question
                    break

# extract QALD format json file in result.json
extract_json(data, "result.json")
