import json
from get_answer import get_answer

# returns a dict for a single question
def build_qald(id: int, q) -> dict:

    question = [
  {
    "language": q["language"],
    "string": q["question"]
  }
]

    query = {
  "sparql": q["query"]
}

    answers = [
  q["answer"]
]

    q = {
    "id": str(id),
    "question": question,
    "query": query,
    "answers": answers
  }

    return q
    

def extract_QALD(question_query:list()):
    questions = {"questions": []}
    id = 1
    for q, query in question_query:
      questions["questions"].append(build_question(id, q, query))
      id += 1
    with open('result.json', 'w') as fp:
        json.dump(questions, fp)
    print("results are exported in "+filename)

def transform_QALD(results):
  with open(results, "w") as file:
    data = json.load(file)
    data.update(a_dictionary)
    file.seek(0)
    json.dump(data, file)