"""Convert the LCQald dataset into qald format for Gerbil evaluation."""
import json
from typing import Any

from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException


def load_lcqald(lcqald: str) -> list:
    """Load the LCQald dataset.

    Parameters
    ----------
    lcqald : str
        Path to the LCQald dataset.

    Returns
    -------
    lcqald_data : list
    """
    with open(lcqald, encoding="utf-8") as f:
        data = json.load(f)
    return data


def build_qald(lcqald_data_content: list) -> dict[str, Any]:
    """Build the qald dataset.

    Parameters
    ----------
    lcqald_data_content : list
        Content of the LCQald dataset as a list.

    Returns
    -------
    qald_dict : dict
        Content of the lcqald dataset as a dict in qald format.
    """
    qald_dict = {}
    qald_dict["dataset"] = {"id": "lcqald-test"}
    questions = []
    for q in lcqald_data_content:
        _id = q["_id"]
        print(f"converting {_id}")
        q_dict = {
            "id": q["_id"],
            "question": [
                {
                    "language": "en",
                    "string": q["corrected_question"],
                }
            ],
            "query": {"sparql": q["sparql_query"]},
            "answers": [get_answer(q["sparql_query"])],
        }
        questions.append(q_dict)
    qald_dict["questions"] = questions  # type: ignore
    return qald_dict


def get_answer(sparql_query: str) -> dict:
    """Get the answer from the SPARQL endpoint.

    Parameters
    ----------
    sparql_query : str
        SPARQL query.

    Returns
    -------
    answer : dict
        Answer from the SPARQL endpoint.
    """
    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(sparql_query)
        answer = sparql.query().convert()
    except SPARQLWrapperException as exception:
        print("SPARQLWrapperException", exception)
        return dict()
    return answer


def save_qald(qald_dict: dict, qald_file: str) -> None:
    """Save the qald dataset.

    Parameters
    ----------
    qald_dict : dict
        Content of the qald dataset as a dict.
    qald_file : str
        Path to the output file.
    """
    with open(qald_file, "w", encoding="utf-8") as f:
        json.dump(qald_dict, f)


lcqald_path = "/Users/mengshima/GitRepos/KBQA-PG/KBQA/datasets/lc-quad-test.json"
lcqald_data = load_lcqald(lcqald_path)
qald = build_qald(lcqald_data)
save_qald(qald, "lcqald-test.json")
