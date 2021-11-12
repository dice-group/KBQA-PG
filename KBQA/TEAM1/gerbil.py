import json
from get_answer import get_answer

# returns a dict for a single question
def build_question(id: int, question_text: str, query_text: str) -> dict:

    question = [
  {
    "language": "en",
    "string": question_text
  }
]

    query = {
  "sparql": query_text
}

    answers = [
  get_answer(query_text)
]

    q = {
    "id": str(id),
    "question": question,
    "query": query,
    "answers": answers
  }

    return q
    

def extract_json(question_query:list(), filename="result.json"):
    questions = {"questions": []}
    id = 1
    for q, query in question_query:
      questions["questions"].append(build_question(id, q, query))
      id += 1
    with open('result.json', 'w') as fp:
        json.dump(questions, fp)
    print("results are exported in "+filename)