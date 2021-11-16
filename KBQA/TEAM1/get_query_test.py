from get_answer import get_answer
from get_query import QA_query_generation

question = "capital of China?"

query_generator = QA_query_generation()

for query in query_generator.get_query(question):
    print("trying query: " + query)
    get_answer(query)

"""
get from console:

The considered words are:
capital, germany


trying query: SELECT ?s WHERE { ?s <https://dbpedia.org/ontology/capital> <https://dbpedia.org/resource/germany> }
get query:
SELECT ?s WHERE { ?s <https://dbpedia.org/ontology/capital> <https://dbpedia.org/resource/germany> }
results:
trying query: SELECT ?o WHERE { <https://dbpedia.org/ontology/capital> <https://dbpedia.org/resource/germany> ?o }
get query:
SELECT ?o WHERE { <https://dbpedia.org/ontology/capital> <https://dbpedia.org/resource/germany> ?o }
results:
trying query: SELECT ?s WHERE { ?s <https://dbpedia.org/ontology/germany> <https://dbpedia.org/resource/capital> }
get query:
SELECT ?s WHERE { ?s <https://dbpedia.org/ontology/germany> <https://dbpedia.org/resource/capital> }
results:
trying query: SELECT ?o WHERE { <https://dbpedia.org/ontology/germany> <https://dbpedia.org/resource/capital> ?o }
get query:
SELECT ?o WHERE { <https://dbpedia.org/ontology/germany> <https://dbpedia.org/resource/capital> ?o }
results:
"""

"""
the query which works for this question:
SELECT ?o WHERE { <http://dbpedia.org/resource/Germany> dbo:capital ?o }
"""
