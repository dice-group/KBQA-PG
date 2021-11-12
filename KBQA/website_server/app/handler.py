from rdflib import URIRef


def process_question(question, app):
    """
    Handle an incoming question and format the answers
    """

    # POST to nginx to get answer_QALD

    # Example answers
    if app == 'A':
        answer_QALD = {
            "questions": [{
                "id": "1",
                "question": [{
                    "language": "en",
                    "string": "Which German cities have more than 250000 inhabitants?"
                }],
                "query": {
                    "sparql": "SELECT DISTINCT ?uri WHERE { { ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/City> . } UNION { ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Town> . }  ?uri <http://dbpedia.org/ontology/country> <http://dbpedia.org/resource/Germany> .  ?uri <http://dbpedia.org/ontology/populationTotal> ?population .  FILTER ( ?population > 250000 ) } "
                },
                "answers": [{
                    "head": {
                        "vars": [
                            "uri"
                        ]
                    },
                    "results": {
                        "bindings": [{
                            "uri": {
                                "type": "uri",
                                "value": "http://dbpedia.org/resource/A"
                            }
                        }]
                    }
                }]
            }]
        }
    if app == 'B':
        answer_QALD = {
            "questions": [{
                "id": "1",
                "question": [{
                    "language": "en",
                    "string": "Which German cities have more than 250000 inhabitants?"
                }],
                "query": {
                    "sparql": "SELECT DISTINCT ?uri WHERE { { ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/City> . } UNION { ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Town> . }  ?uri <http://dbpedia.org/ontology/country> <http://dbpedia.org/resource/Germany> .  ?uri <http://dbpedia.org/ontology/populationTotal> ?population .  FILTER ( ?population > 250000 ) } "
                },
                "answers": [{
                    "head": {
                        "vars": [
                            "uri"
                        ]
                    },
                    "results": {
                        "bindings": [{
                            "uri": {
                                "type": "uri",
                                "value": "http://dbpedia.org/resource/B"
                            }
                        }]
                    }
                }]
            }]
        }

    answer_parsed = parse_answer(answer_QALD['questions'][0]['answers'][0], 'uri')

    return answer_parsed


def parse_answer(db_answer, prop_ans):
    """
    Parse the result from DBpedia and extract the answer for the searched property
    """

    answers = []
    for i in range(len(db_answer['results']['bindings'])):
        if db_answer['results']['bindings'][i][prop_ans]['type'] == 'uri':
            resource = URIRef(db_answer['results']['bindings'][i][prop_ans]['value'])
            string_value = resource.n3()
            answers.append(string_value)
        else:
            answers.append(db_answer['results']['bindings'][i][prop_ans]['value'])
    answer = ", ".join(str(x) for x in answers)

    return answer
