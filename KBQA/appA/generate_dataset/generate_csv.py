"""Generate csv files for the QALD dataset."""
import csv
import json
from json.decoder import JSONDecodeError

import requests

REPLACEMENT = [
    ["?", "var_"],
    [" . ", " sep_dot "],
    ["{", "brack_open"],
    ["}", "brack_close"],
    ["http://dbpedia.org/property/", "dbp_"],
    ["http://dbpedia.org/resource/", "dbr_"],
    ["http://dbpedia.org/ontology/", "dbo_"],
    ["<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>", "rdf_type"],
    [" <", " "],
    ["> ", " "],
    [" <<", " <"],
    [">> ", "> "],
]


def read_json(file: str) -> dict:
    """Reads a json file and returns the content as a dict.

    Parameters
    ----------
    file : str
        Path to the json file.

    Returns
    -------
    qald : dict
        Content of the json file as a dict.
    """
    with open(file, "r", encoding="utf8") as f:
        qald = json.load(f)
    return qald


def output_csv(file: str, ques_query_list: list) -> None:
    """Outputs a csv file with the question and query.

    Parameters
    ----------
    file : str
        Path to the output file.
    ques_query_list : list
        List of tuples with the question and query.
    """
    with open(file, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(ques_query_list)


def extract_lcqald_question_query(dataset_json: dict) -> list:
    """Extracts the question and query from the LCQald dataset.

    Parameters
    ----------
    dataset_json : dict
        Content of the LCQald dataset as a dict.

    Returns
    -------
    dataset : list
        List of tuples with the question and query.
    """
    dataset = []
    for questions in dataset_json:
        dataset.append([questions["corrected_question"], questions["sparql_query"]])
    return dataset


def extract_qald_question_query(dataset_json: dict, language="en") -> list:
    """Extracts the question and query from the QALD dataset.

    Parameters
    ----------
    dataset_json : dict
        Content of the QALD dataset as a dict.
    language : str
        Language of the question.

    Returns
    -------
    dataset : list
        List of tuples with the question and query.
    """
    dataset = []
    for question in dataset_json["questions"]:
        for q in question["question"]:
            if q["language"] == language:
                query = question["query"]["sparql"]
                query = query.replace("res:", "http://dbpedia.org/resource/")
                query = query.replace("dbp:", "http://dbpedia.org/property/")
                query = query.replace("dbo:", "http://dbpedia.org/ontology/")
                query = query.replace(
                    "rdf:type", "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
                    )
                dataset.append([q["string"], query])
    return dataset


def query_dbspotlight(question: str, language: str = "en", confidence: float = 0.5) -> dict:
    """Query the endpoint of DBspotlight for entity recognition.

    Parameters
    ----------
    question : str
        Natural language question.
    language : str
        Language of the question.
    confidence : float, optional
        Lower bound for the confidence of recognized entities (default: 0.5).

    Returns
    -------
    response : dict
        Response of the DBspotlight endpoint without any processing
        as JSON dict.
    """
    endpoint = f"https://api.dbpedia-spotlight.org/{language}/annotate/"

    try:
        response = requests.post(
            endpoint,
            headers={"Accept": "application/json"},
            data={"text": question, "confidence": confidence},
        ).json()
    except JSONDecodeError:
        print("It was not possible to parse the answer.")

        return dict()

    return response


def replace_symbols(query: str) -> str:
    """Replaces symbols in a query.

    Parameters
    ----------
    query : str
        Query with symbols.

    Returns
    -------
    query : str
        Query without symbols.
    """
    for symbol, name in REPLACEMENT:
        query = query.replace(symbol, name)
    return query


def replace_entities_in_question_and_query_qald(dataset: list) -> list:
    """Replaces entities in the question and query of the QALD dataset.

    Parameters
    ----------
    dataset : list
        List of tuples with the question and query.

    Returns
    -------
    dataset : list
        List of tuples with the question and query with placeholders.
    """
    dataset_ph = []
    for question, query in dataset:
        entities = query_dbspotlight(question, confidence=0.1)
        question_ph, query_ph = question, query
        if "Resources" in entities.keys():
            for entity in entities["Resources"]:
                uri = entity["@URI"]
                surface = entity["@surfaceForm"]
                placeholder = 65
                if uri in query_ph:
                    query_ph = query_ph.replace(uri, "<<" + chr(placeholder) + ">>")
                    question_ph = question_ph.replace(
                        surface, "<" + chr(placeholder) + ">"
                        )
                    placeholder += 1
            query_ph = replace_symbols(query_ph)
            dataset_ph.append([question_ph, query_ph])
    return dataset_ph


def replace_entities_in_question_and_query_lcqald(dataset: list) -> list:
    """Replaces entities in the question and query of the LCQald dataset.

    Parameters
    ----------
    dataset : list
        List of tuples with the question and query.

    Returns
    -------
    dataset : list
        List of tuples with the question and query with placeholders.
    """
    dataset_ph = []
    for question, query in dataset:
        entities = query_dbspotlight(question, confidence=0.1)
        question_ph, query_ph = question, query
        if "Resources" in entities.keys():
            for entity in entities["Resources"]:
                uri = entity["@URI"]
                surface = entity["@surfaceForm"]
                placeholder = 65
                if uri in query_ph:
                    query_ph = query_ph.replace(uri, "<" + chr(placeholder) + ">")
                    question_ph = question_ph.replace(
                        surface, "<" + chr(placeholder) + ">"
                        )
                    placeholder += 1
            query_ph = replace_symbols(query_ph)
            dataset_ph.append([question_ph, query_ph])
    return dataset_ph


def delete_prefixes(dataset: list) -> list:
    """Deletes prefixes in queries of the QALD dataset.

    Parameters
    ----------
    dataset : list
        List of tuples with the question and query.

    Returns
    -------
    dataset : list
        List of tuples with the question and query without prefixes.

    """
    dataset_ = []
    for question, query in dataset:
        try:
            query = query[query.index("SELECT") :]
        except ValueError:
            query = query[query.index("ASK") :]
        dataset_.append([question, query])
    return dataset_


def convert_lcqald(lcqald_path: str, output_file: str) -> None:
    """Converts the LCQald dataset to a CSV file.

    Parameters
    ----------
    lcqald_path : str
        Path to the LCQald dataset.
    output_file : str
        Path to the output file.
    """
    dataset = read_json(lcqald_path)
    dataset = extract_lcqald_question_query(dataset)
    dataset_ph = replace_entities_in_question_and_query_lcqald(dataset)
    output_csv(output_file, dataset_ph)


def convert_qald(qald_path: str, output_file: str, language="en") -> None:
    """Converts the QALD dataset to a CSV file.

    Parameters
    ----------
    qald_path : str
        Path to the QALD dataset.
    output_file : str
        Path to the output file.
    language : str, optional
        Language of the dataset (default: "en").
    """
    qald9 = read_json(qald_path)
    qald9 = extract_qald_question_query(qald9, language)
    qald9_ph = replace_entities_in_question_and_query_qald(qald9)
    qald9_ph = delete_prefixes(qald9_ph)
    output_csv(output_file, qald9_ph)


lcqald_filepath = "/Users/mengshima/GitRepos/KBQA-PG/KBQA/datasets/lc-quad-train.json"
qald9_filepath = "/Users/mengshima/GitRepos/KBQA-PG/KBQA/datasets/updated-qald-9-train-multilingual.json"

convert_lcqald(lcqald_filepath, "lcqald_ph.csv")
convert_qald(qald9_filepath, "qald9_ph_de.csv", "de")
