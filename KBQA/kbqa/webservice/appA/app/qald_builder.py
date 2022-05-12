"""Module to create a QALD json string for given inputs."""
from typing import Any
from typing import Dict


def qald_builder_select_answer(
    sparql_query: str, answer: Dict, question: str, language: str
) -> Dict[str, Any]:
    """Build a QALD-string with the given parameters for a SELECT query.

    Parameters
    ----------
    sparql_query : str
        Generated SPARQL-query for the question used to find the answers.
    answer : dict
        Answer from DBpedia in the JSON format for a SELECT query.
    question : str
        The natural language question.
    language : str
        Language tag.

    Returns
    -------
    qald_string : dict
        Dictionary formatted in the QALD format.
    """
    # id-Object
    json_id = {"id": "1"}

    # question-Object
    json_question = {"question": [{"language": language, "string": question}]}

    # query-Object
    json_query = {"query": {"sparql": sparql_query}}

    # answers-Object
    json_answers: Dict = {"answers": []}

    converted_answer = convert_dbpedia_answer_to_gerbil_format(answer)

    json_answers["answers"].append(converted_answer)

    # Combined-Object
    questions_obj = {
        "id": json_id["id"],
        "question": json_question["question"],
        "query": json_query["query"],
        "answers": json_answers["answers"],
    }

    # Question-Object
    json_questions: Dict = {"questions": []}

    json_questions["questions"].append(questions_obj)

    return json_questions


def qald_builder_ask_answer(
    sparql_query: str, answer: Dict, question: str, language: str
) -> Dict[str, Any]:
    """Build a QALD-string with the given parameters for an ASK query.

    Parameters
    ----------
    sparql_query : str
        Generated SPARQL-query for the question used to find the answers.
    answer : dict
        Answer from DBpedia in the JSON format for an ASK query.
    question : str
        The natural language question.
    language : str
        Language tag.

    Returns
    -------
    qald_str : dict
        Dictionary formatted in the QALD format.
    """
    json_id = {"id": "1"}

    json_question = {"question": [{"language": language, "string": question}]}

    json_query = {"query": {"sparql": sparql_query}}

    boolean_value = answer["boolean"]

    json_answers = {"answers": [{"boolean": boolean_value}]}

    questions_obj = {
        "id": json_id["id"],
        "question": json_question["question"],
        "query": json_query["query"],
        "answers": json_answers["answers"],
    }

    json_questions: Dict = {"questions": []}
    json_questions["questions"].append(questions_obj)

    return json_questions


def qald_builder_empty_answer(
    sparql_query: str, question: str, language: str
) -> Dict[str, Any]:
    """Build a QALD-string with the given parameters if no answers are found.

    Parameters
    ----------
    sparql_query : str
        Generated SPARQL-query for the question used to find the answers.
    question : str
        The natural language question.
    language : str
        Language tag.

    Returns
    -------
    qald_string : dict
        Dictionary formatted in the QALD format.
    """
    # id-Object
    json_id = {"id": "1"}

    # question-Object
    json_question = {"question": [{"language": language, "string": question}]}

    # query-Object
    json_query = {"query": {"sparql": sparql_query}}

    # answers-Object
    json_answers: Dict = {
        "answers": [{"head": {"vars": []}, "results": {"bindings": []}}]
    }

    # Combined-Object
    questions_obj = {
        "id": json_id["id"],
        "question": json_question["question"],
        "query": json_query["query"],
        "answers": json_answers["answers"],
    }

    # Question-Object
    json_questions: Dict = {"questions": []}

    json_questions["questions"].append(questions_obj)

    return json_questions


def convert_dbpedia_answer_to_gerbil_format(answer: Dict) -> Dict[str, Dict[str, Any]]:
    """Convert a JSON-answer from DBpedia to a JSON-string, which is accepted by Gerbil.

    Since Gerbil does not support all keys of the response from DBpedia, only the
    needed parts are extracted. The needed parts are "vars" and "bindings".

    Parameters
    ----------
    answer : dict
        JSON-response from DBpedia as a dictionary.

    Returns
    -------
    converted_answer : dict
        Dictionary, which only contains the vars and the bindings as keys.
    """
    # vars object
    variables = answer["head"]["vars"]

    # bindings
    bindings = answer["results"]["bindings"]

    converted_answer = {"head": {"vars": variables}, "results": {"bindings": bindings}}

    return converted_answer


