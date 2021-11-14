import json
from get_answer import get_answer

# returns a dict for a single question
def build_qald(questions) -> dict:
    results = []
    for q in questions:
      question = [
    {
      "language": q["language"],
      "string": q["question"]
    }
  ]

      quest = {
      "id": q["id"],
      "question": question,
      "query": q["query"],
      "answers": q["answer"]
    }
      results.append(quest)

    return {"questions":results}
    

def extract_json(result, filename="result.json"):
    with open(filename, 'w') as fp:
        json.dump({"questions":result}, fp)
    print("results are exported")
