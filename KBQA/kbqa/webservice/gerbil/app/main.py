"""GERBIL Evaluation for QA systems."""

import json
import os
from pathlib import Path
import time
from typing import List

from app.approach import Approach
from app.converter import summarize_results
import pandas as pd
from pandas.core.frame import DataFrame
import requests
from requests import RequestException

all_datasets = [
    "LCQUAD",
    "NLQ",
    "QALD1 Test DBpedia",
    "QALD1 Test Musicbrainz",
    "QALD1 Train DBpedia",
    "QALD1 Train Musicbrainz",
    "QALD3 Test DBpedia",
    "QALD3 Train DBpedia",
    "QALD4 Test Hybrid",
    "QALD4 Test Multilingual",
    "QALD4 Train Hybrid",
    "QALD4 Train Multilingual",
    "QALD5 Test Hybrid",
    "QALD5 Test Multilingual",
    "QALD5 Train Hybrid",
    "QALD5 Train Multilingual",
    "QALD6 Test Hybrid",
    "QALD6 Test Multilingual",
    "QALD6 Train Hybrid",
    "QALD6 Train Multilingual",
    "QALD7 Test Multilingual",
    "QALD7 Test Wikidata en",
    "QALD7 Train Hybrid",
    "QALD7 Train Multilingual",
    "QALD7 Train Wikidata en",
    "QALD8 Test Multilingual",
    "QALD8 Train Multilingual",
    "QALD9 Test Multilingual",
    "QALD9 Train Multilingual",
]  # "DBpedia Entity INEX","DBpedia Entity QALD2","DBpedia Entity SemSearch","DBpedia Entity TREC Entity" can not be loaded

# all_datasets = ["QALD9 Test Multilingual"] # DEBUG


def start_experiment(
    system_name: str,
    system_url: str,
    gerbil_url: str = "http://gerbil-qa.aksw.org/gerbil",
    datasets: List[str] = all_datasets,
    language: str = "en",
) -> int:
    """Start a GERBIL experiment of the given system and dataset.

    Parameters
    ----------
    system_name : str
        Name of the QA system, shown on the Website
    system_url : str
        URL to the evaluated QA system
    gerbil_url : str, optional
        Base URL of the used GERBIL system, by default "http://gerbil-qa.aksw.org/gerbil"
    datasets : List[str], optional
        List of datasets the system is evaluated on, by default all_datasets
    language : str, optional
        Used language for evaluation, by default "en"

    Returns
    -------
    int
        [description]
    """
    url = f"{gerbil_url}/execute"
    experiment_data = {
        "type": "QA",
        "matching": "STRONG_ENTITY_MATCH",
        "annotator": [f"{system_name}({system_url})"],
        "dataset": datasets,
        "answerFiles": [],
        "questionLanguage": language,
    }
    param = {"experimentData": json.dumps(experiment_data)}
    gerbil_id = 0

    try:
        html = requests.get(url, params=param).content
        gerbil_id = int(html)
    except RequestException as exception:
        print(exception)
        return gerbil_id

    return gerbil_id


def get_evaluation(gerbil_id: int, gerbil_url: str) -> DataFrame:
    """Get the evaluation result of the given GERBIL experiment.

    Parameters
    ----------
    gerbil_id : int
        ID of the GERBIL experiment
    gerbil_url : str
        Base URL of the used GERBIL system

    Returns
    -------
    DataFrame
        Evaluation result
    """
    if not gerbil_id:
        return None

    # id = 202201230018  # DEBUG
    # id = 202112140000
    url = f"{gerbil_url}/experiment?id={gerbil_id}"

    try:
        html = requests.get(url)
        df_list = pd.read_html(html.content)
        results = df_list[0]
        macro_f1 = results.iloc[0]["Macro F1"]
        print(macro_f1)
    except RequestException as exception:
        print(exception)
        return None

    # print(html.text)
    if "The annotator caused too many single errors." in html.text:
        print(f"Experiment {gerbil_id} could not be executed.")
        return None
    elif "The experiment is still running." in html.text:
        time.sleep(60)
        return get_evaluation(gerbil_id, gerbil_url)
    else:
        return results


def startup() -> None:
    """Handle GERBIL evaluation for our systems."""
    commit = os.environ.get("GITHUB_SHA")
    print(f"Commit {commit}")

    approaches = [Approach("appA"), Approach("appB")]
    # approaches = [Approach("appB")]  # DEBUG
    # approaches = []

    gerbil_system = "http://gerbil-qa.aksw.org/gerbil"  # official
    gerbil_system = "http://gerbil-qa.cs.upb.de:8080/gerbil"  # DICE group

    for approach in approaches:
        approach.experiment_id = start_experiment(
            approach.experiment_name, approach.url, gerbil_system
        )
        print(f"Start experiment {approach.experiment_id} of {approach.name}.")

    for approach in approaches:
        path = f"/evaluation/{approach.name}"
        Path(path).mkdir(parents=True, exist_ok=True)
        result = get_evaluation(approach.experiment_id, gerbil_system)

        if result is not None:
            result.to_csv(f"{path}/{commit}-{approach.experiment_id}.csv")
            result.to_html(f"{path}/{commit}-{approach.experiment_id}.html")

        summarize_results(approach)
