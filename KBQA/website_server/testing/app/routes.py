from app import application
from flask import request


@application.route('/AppA', methods=['POST'])
def questionA():
    asked_question = request.form['query']
    print('Question', asked_question)

    answers = {
            "questions": [{
                "id": "1",
                "question": [{
                    "language": "en",
                    "string": asked_question
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
                            "string": {
                                "type": "string",
                                "value": "Question = " + asked_question + ", App = A"
                            }
                        }]
                    }
                }]
            }]
        }

    return answers


@application.route('/AppB', methods=['POST'])
def questionB():
    asked_question = request.form['query']
    print('Question', asked_question)

    answers = {
            "questions": [{
                "id": "1",
                "question": [{
                    "language": "en",
                    "string": asked_question
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
                            "string": {
                                "type": "string",
                                "value": "Question = " + asked_question + ", App = B"
                            }
                        }]
                    }
                }]
            }]
        }

    return answers
