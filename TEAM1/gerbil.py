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
    

def extract_json(result):
    questions = {"questions": [result]}
    with open('result.json', 'w') as fp:
        json.dump(questions, fp)
    print("results are exported")
