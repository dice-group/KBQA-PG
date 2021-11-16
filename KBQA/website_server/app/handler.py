from rdflib import URIRef
import requests


def process_query(query, app):
    """
    Handle an incoming query and format the answers.
    """

    # Ask the webserver for an answer the the query using approach "app"
    webserver_address = "http://localhost:24804{dir}"
    if app == "A":
        r = requests.post(webserver_address.format(dir="/AppA"), data={"query": query})
    else:
        r = requests.post(webserver_address.format(dir="/AppB"), data={"query": query})
    response_QALD = r.json()
    answers = parse_response(response_QALD)

    return answers


def parse_response(QALD):
    """
    Parse a QALD dictionary to get an appropriate answer string.
    """
    bindings = QALD["questions"][0]["answers"][0]["results"]["bindings"]
    bindings_string_list = []
    for i in range(len(bindings)):
        key = list(bindings[i])[0]  # Get the key name
        if bindings[i][key]["type"] == "uri":
            resource = URIRef(bindings[i][key]["value"])
            string_value = resource.n3()
            bindings_string.append(string_value)
        else:
            bindings_string_list.append(bindings[i][key]["value"])
    answers_string = ", ".join(str(x) for x in bindings_string_list)

    return answers_string


# Example QALD dictionary
# {
#             "questions": [{
#                 "id": "1",
#                 "question": [{
#                     "language": "en",
#                     "string": asked_question
#                 }],
#                 "query": {
#                     "sparql": "SELECT DISTINCT ?uri WHERE { { ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/City> . } UNION { ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Town> . }  ?uri <http://dbpedia.org/ontology/country> <http://dbpedia.org/resource/Germany> .  ?uri <http://dbpedia.org/ontology/populationTotal> ?population .  FILTER ( ?population > 250000 ) } "
#                 },
#                 "answers": [{
#                     "head": {
#                         "vars": [
#                             "uri"
#                         ]
#                     },
#                     "results": {
#                         "bindings": [{
#                             "string": {
#                                 "type": "string",
#                                 "value": "Question = " + asked_question + ", App = A"
#                             }
#                         }]
#                     }
#                 }]
#             }]
#         }
