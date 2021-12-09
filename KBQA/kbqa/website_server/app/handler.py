import json

import requests


def process_question(question, app):
    """
    Handle an incoming query and format the answers.
    """

    # Ask the webserver for an answer the the query using approach "app"
    webserver_address = "http://nginx{dir}"

    if app == "A":
        r = requests.post(
            webserver_address.format(dir="/appA/"), data={"query": question}
        )
    else:
        r = requests.post(
            webserver_address.format(dir="/appB/"), data={"query": question}
        )

    response_json = json.loads(r.text)
    bindings, query = extract_bindings_from_QALD(response_json)
    answers = format_bindings(bindings)

    return answers, query


def extract_bindings_from_QALD(QALD):
    """
    Parse a QALD dictionary to get an appropriate answer string.
    """

    results = list()

    questions = QALD["questions"]

    for quest in questions:
        question = quest["question"]
        query = quest["query"]
        answers = quest["answers"]

        print("Question:", question)
        print("Query:", query)

        for answer in answers:
            variables = answer["head"]["vars"]

            bindings = answer["results"]["bindings"]

            for var in variables:
                for binding in bindings:
                    result_type = binding[var]["type"]
                    result_value = binding[var]["value"]

                    result = (result_type, result_value)

                    results.append(result)

    return results, query["sparql"]


def format_bindings(bindings):
    results = list()

    # no bindings, i.e. no answers found
    if len(bindings) == 0:
        return ["No answer found"]

    for binding in bindings:
        if binding[0] == "uri":
            entity = binding[1].split("/")[-1]
            formated_result = entity.replace("_", " ")

            results.append(formated_result)
        else:
            results.append(binding[1])

    return results
