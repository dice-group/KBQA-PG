"""GERBIL Evaluation for QA systems."""

import json
import os
from pathlib import Path
import time
from typing import List

from app.config import approaches
from app.config import encode_experiment_filename
from app.config import gerbil_datasets
from app.config import gerbil_systems
from app.converter import summarize_results
import pandas as pd
from pandas.core.frame import DataFrame
import requests
from requests import RequestException


def start_experiment(
    system_name: str,
    system_url: str,
    gerbil_url: str = "{}/gerbil".format(
        gerbil_systems["aksw"]
    ),  # pylint: disable=consider-using-f-string
    datasets: List[str] = gerbil_datasets,
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


def evaluate_approaches(gerbil_system: str) -> None:
    """Handle GERBIL evaluation for our systems.

    :param gerbil_system: Key of GERBIL system that should be used
    :type gerbil_system: str
    """
    commit_id = os.environ.get("GITHUB_SHA") or "local"
    print(f"Commit {commit_id}")

    gerbil_system_url = gerbil_systems[gerbil_system]

    # approaches = [Approach("appB")]  # DEBUG
    # approaches = []

    for approach in approaches:
        approach.experiment_id = start_experiment(
            approach.experiment_name, approach.url, gerbil_system_url
        )
        print(f"Start experiment {approach.experiment_id} of {approach.name}.")

    for approach in approaches:
        path = f"/evaluation/{approach.name}"
        Path(path).mkdir(parents=True, exist_ok=True)
        result = get_evaluation(approach.experiment_id, gerbil_system_url)

        if result is not None:
            filename = encode_experiment_filename(
                approach.experiment_id, gerbil_system, commit_id
            )
            result.to_csv(f"{path}/{filename}.csv")
            result.to_html(f"{path}/{filename}.html")

        summarize_results(approach)
