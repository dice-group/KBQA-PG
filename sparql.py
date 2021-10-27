# you have to install SPARQLWrapper library first! 
# pip install SPARQLWrapper

from SPARQLWrapper import SPARQLWrapper, JSON
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
    PREFIX dbprop: <http://dbpedia.org/ontology/>
PREFIX db: <http://dbpedia.org/resource/>
SELECT ?who, ?WORK, ?genre WHERE {
  db:Tokyo_Mew_Mew dbprop:author ?who . 
  ?WORK  dbprop:author ?who .
OPTIONAL { ?WORK dbprop:genre ?genre } .
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print(result["who"], result["WORK"], result.get("genre", None))