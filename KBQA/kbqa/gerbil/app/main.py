import json
from pathlib import Path
import time

import pandas as pd
from pandas.core.frame import DataFrame
import requests


def start_experiment(
    system_name: str,
    system_url: str,
    datasets: list[str] = ["QALD9 Train Multilingual"],
    language: str = "en",
) -> int:
    """Start a GERBIL experiment of the given system and dataset

    Args:
        system_name (str): Name of the QA system, shown on the Website
        system_url (str): URL to the evaluated QA system
        datasets (list[str], optional): List of datasets the systen is evaluated on. Defaults to ["QALD9 Train Multilingual"].
        language (str, optional): Used language for evaluation. Defaults to "en".

    Returns:
        (int): Id of the started GERBIL experiment
    """
    url = "http://gerbil-qa.aksw.org/gerbil/execute"
    experiment_data = {
        "type": "QA",
        "matching": "STRONG_ENTITY_MATCH",
        "annotator": ["{}({})".format(system_name, system_url)],
        "dataset": datasets,
        "answerFiles": [],
        "questionLanguage": language,
    }
    param = {"experimentData": json.dumps(experiment_data)}

    try:
        html = requests.get(url, params=param).content
        id = int(html)
    except Exception as e:
        print(e)
        return 0

    return id


def get_test_result(id: int) -> DataFrame:
    """Get the evaluation result of the given GERBIL experiment

    :param id: Id of the GERBIL experiment
    :type id: int
    :return: Evaluation result
    :rtype: DataFrame
    """
    if not id:
        return None

    url = "http://gerbil-qa.aksw.org/gerbil/experiment?id={}".format(id)

    try:
        html = requests.get(url).content
        df_list = pd.read_html(html)
        df = df_list[0]
        macro_f1 = df.iloc[0]["Macro F1"]
        print(macro_f1)
    except Exception as e:
        print(e)
        return None

    if macro_f1 == "The experiment is still running.":
        time.sleep(60)
        return get_test_result(id)
    else:
        Path("experiments").mkdir(parents=True, exist_ok=True)
        df.to_csv("experiments/latest.csv")
        df.to_html("experiments/latest.html")
        return df


def main():
    """Handle GERBIL evaluation for our systems"""
    qa_name = "NIFWS_KBQA-PG-AppA"
    qa_uri = "http://kbqa-pg.cs.upb.de/appA/"

    id = start_experiment(qa_name, qa_uri)
    print(id)
    df = get_test_result(id)
    print(df)
