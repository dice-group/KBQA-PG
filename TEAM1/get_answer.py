from SPARQLWrapper import SPARQLWrapper, JSON
import ssl


# pass the query in the function
# return results as dictionary
def get_answer(query:str) -> dict:
  # to avoid [SSL: CERTIFICATE_VERIFY_FAILED] error
  ssl._create_default_https_context = ssl._create_unverified_context
  print("get query: ")
  print(query)
  sparql = SPARQLWrapper("http://dbpedia.org/sparql")
  sparql.setQuery(query)
  sparql.setReturnFormat(JSON)
  # sparql.query() returns HTML response
  # convert() converts response to dictionary 
  answers = sparql.query().convert()
  # print(answers)
  # print("results: ")
  # print_result(answers)
  return answers

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




