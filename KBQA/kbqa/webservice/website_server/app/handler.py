"""Module to handle inputs from the website and return the answers."""
import json
from typing import Dict
from typing import List
from typing import Tuple

from flask import abort
import requests


def process_question(question: str, app: str) -> Tuple[List[str], str]:
    """Handle an incoming query and format the answers.

    Parameters
    ----------
    question : str
        Natural language question asked by an enduser.
    app : str
        Chosen approach by an enduser (should be A or B).

    Returns
    -------
    answers : list
        List of natural language answers for the asked question.
    query : str
        Generated SPARQL-query used to find the answers.

    Raises
    ------
    ValueError
        If app is not 'A' or 'B'.
    """
    # Ask the webserver for an answer for the query using approach "app"
    webserver_address = "http://nginx{dir}"

    if app == "A":
        response = requests.post(
            webserver_address.format(dir="/appA/"), data={"query": question}
        )
    elif app == "B":
        response = requests.post(
            webserver_address.format(dir="/appB/"), data={"query": question}
        )
    else:
        raise ValueError("Approach should be A or B.")

    if response.status_code == 500:
        abort(500, description="There seems to be a problem in the endpoint")

    if response.status_code == 502:
        abort(502, description="The endpoint is not reachable for the moment")

    if response.status_code == 504:
        abort(504, description="The endpoint is taking too long to find an answer")

    response_json = json.loads(response.text)
    bindings, query = extract_bindings_from_qald(response_json)
    answers = format_bindings(bindings)

    return answers, query


def extract_bindings_from_qald(qald: Dict) -> Tuple[List[Tuple[str, str]], str]:
    """Parse a QALD dictionary to get answers as resources.

    Parameters
    ----------
    qald : dict
        The QALD-string as a dict.

    Returns
    -------
    answers : list
        List of answers. An answer is described by a tuple (type, resource),
        where type is the DBpedia-type and resource the DBpedia-resource.
    query : str
        Generated SPARQL-query used to find the answers.
    """
    questions = qald["questions"]

    for quest in questions:
        query = quest["query"]
        answers = quest["answers"]

        for answer in answers:
            if "boolean" in answer.keys():
                results = extract_results_from_boolean(answer)
            else:
                results = extract_results_from_variable(answer)

    return results, query["sparql"]


def extract_results_from_boolean(answer: Dict) -> List[Tuple[str, str]]:
    """Extract the results from a boolean answer.

    Parameters
    ----------
    answer : dict
        The answer as a dict.

    Returns
    -------
    answers : list
        List of answers. An answer is described by a tuple.
    """
    return [("", answer["boolean"])]


def extract_results_from_variable(answer: Dict) -> List[Tuple[str, str]]:
    """Extract the results from a variable answer.

    Parameters
    ----------
    answer : dict
        The answer as a dict.

    Returns
    -------
    answers : list
        List of answers. An answer is described by a tuple (type, value).
    """
    results = []

    variables = answer["head"]["vars"]

    bindings = answer["results"]["bindings"]

    for var in variables:
        for binding in bindings:
            result_type = binding[var]["type"]
            result_value = binding[var]["value"]

            result = (result_type, result_value)

            results.append(result)
    return results


def format_bindings(bindings: List[Tuple[str, str]]) -> List[str]:
    """Format the resources into natural language strings.

    Given a list of bindings from DBpedia format these bindings into
    simple strings, which can be displayed on the website
    (e.g. http://dbpedia.org/resource/Germany -> Germany)

    Parameters
    ----------
    bindings : list
        List of DBpedia-resources returned from the function
        extract_bindings_from_qald.

    Returns
    -------
    results : list
        List of natural language answers extracted from the given
        DBpedia-resources.
    """
    results = []

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
