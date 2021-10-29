from SPARQLWrapper import SPARQLWrapper, JSON
import ssl
import json

# to avoid [SSL: CERTIFICATE_VERIFY_FAILED] error
ssl._create_default_https_context = ssl._create_unverified_context

# pass the query in the function
# return results as dictionary
def select_query(query:str) -> dict:
  sparql = SPARQLWrapper("http://dbpedia.org/sparql")
  sparql.setQuery(query)
  sparql.setReturnFormat(JSON)
  # sparql.query() returns HTML response
  # convert() converts response to dictionary 
  results = sparql.query().convert()
  # print(results)
  print_result(results)
  return results

# print results for query as:
  # var1: value, var2: value,...
  # var1: value, var2: value,...
def print_result(results: dict):
  vars = results["head"]["vars"]
  for result in results["results"]["bindings"]:
    for var in vars:
      type_value = result.get(var, None)
      if type_value:
        print(var+": "+type_value["value"], end=", ")
    print('')

example_question = '''
  what are the works and the genres of these works, which have the same author as Tokyo Mew Mew
'''

example_query = """
    PREFIX dbprop: <http://dbpedia.org/ontology/>
PREFIX db: <http://dbpedia.org/resource/>
SELECT ?who, ?work, ?genre WHERE {
  db:Tokyo_Mew_Mew dbprop:author ?who . 
  ?work  dbprop:author ?who .
OPTIONAL { ?work dbprop:genre ?genre } .
}
"""

example_question2 = '''
  what are the names of Asturias in other languages
'''

example_query2= """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
"""

example_query3="""
  SELECT ?s WHERE {?s https://dbpedia.org/ontology/languages https://dbpedia.org/resource/Philippines }
"""

# print("example 1: ")
# select_query(example_query)
# print("example 2: ")
# select_query(example_query2)
# print("example 3: ")
# select_query(example_query3)


# this function returns a dict for a single question
def build_question(id: str,question_text: str, query_text: str) -> dict:

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
  select_query(query_text)
]

    q = {
    "id": id,
    "question": question,
    "query": query,
    "answers": answers
  }

    return q
    

def extract_json(questions):
    with open('result.json', 'w') as fp:
        json.dump(questions, fp)

questions = {"questions": []}

q1 = build_question("1", example_question, example_query)
questions["questions"].append(q1)

q2 = build_question("2", example_question2, example_query2)
questions["questions"].append(q2)

extract_json(questions)