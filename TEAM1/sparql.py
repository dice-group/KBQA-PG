# you have to install SPARQLWrapper library first! 
# pip install SPARQLWrapper

from SPARQLWrapper import SPARQLWrapper, JSON
import ssl

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



example_query = """
    PREFIX dbprop: <http://dbpedia.org/ontology/>
PREFIX db: <http://dbpedia.org/resource/>
SELECT ?who, ?work, ?genre WHERE {
  db:Tokyo_Mew_Mew dbprop:author ?who . 
  ?work  dbprop:author ?who .
OPTIONAL { ?work dbprop:genre ?genre } .
}
"""

example_query2= """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
"""

print("example 1: ")
select_query(example_query)
print("example 2: ")
select_query(example_query2)