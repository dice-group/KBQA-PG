from gerbil import extract_json
from get_answer import get_answer


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


# print("example 1: ")
# get_answer(example_query)

# print("example 2: ")
# get_answer(example_query2)

question_query = [
    [example_question, example_query],
    [example_question2, example_query2]
]
extract_json(question_query)

