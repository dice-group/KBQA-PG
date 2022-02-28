"""Module to create a QALD json string for given inputs."""
import json
from typing import Dict


def qald_builder(sparql_query: str, answer: Dict, question: str, language: str) -> str:
    """Build a QALD-string with the given parameters.

    Parameters
    ----------
    sparql_query : str
        Generated SPARQL-query for the question used to find the answers.
    answer : list
        List of DBpedia-resources, which contain the answers for the question.
    question : str
        The natural language question.
    language : str
        Language tag.

    Returns
    -------
    qald_string : str
        JSON string formatted in the QALD format
    """
    # id-Object
    json_id = {"id": "1"}

    # question-Object
    json_question = {"question": [{"language": language, "string": question}]}

    # query-Object
    json_query = {"query": {"sparql": sparql_query}}

    # answers-Object
    json_answers: Dict = {"answers": []}

    json_answers["answers"].append(answer)

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

    return json.dumps(json_questions)


def qald_builder_empty_answer(sparql_query: str, question: str, language: str) -> str:
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
    qald_string : str
        JSON string formatted in the QALD format
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

    return json.dumps(json_questions)
