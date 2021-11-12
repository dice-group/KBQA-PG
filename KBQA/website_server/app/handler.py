from rdflib import URIRef
import requests


def process_question(question, app):
    """
    Handle an incoming question and format the answers
    """

    # Ask the webserver for an answer the the query "question" using approach "app"
    webserver_address = "http://localhost:24804{dir}"
    if app == 'A':
        r = requests.post(webserver_address.format(dir="/AppA"), data={'query': question})
    else:
        r = requests.post(webserver_address.format(dir="/AppB"), data={'query': question})
    answer_QALD = r.json()
    answer_parsed = parse_answer(answer_QALD['questions'][0]['answers'][0], 'string')

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
