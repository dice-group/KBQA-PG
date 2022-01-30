"""Converter for GERBIL results."""

import os
from typing import List

from app.approach import Approach
import pandas as pd
import simplejson


class Experiment:
    """Results of a GERBIL experiment."""

    def __init__(
        self,
        gerbil_id: int,
        gerbil_url: str,
        gerbil_timestamp: str,
        kbqa_name: str,
        kbqa_version: str,
        dataset: str,
        sub_experiments: List["SubExperiment"],
    ) -> None:
        """Store results of a GERBIL experiment.

        Parameters
        ----------
        gerbil_id : int
            ID of the GERBIL experiment
        gerbil_url : str
            Base URL of the used GERBIL system
        gerbil_timestamp : str
            Timestamp of the experiment performed
        kbqa_name : str
            Name of the evaluated KBQA system
        kbqa_version : str
            Version of the evaluated KBQA system
        dataset : str
            Dataset used for evaluation
        sub_experiments : List[SubExperiment]
            List of sub experiments
        """
        self.gerbil_id = gerbil_id
        self.gerbil_url = gerbil_url
        self.gerbil_timestamp = gerbil_timestamp
        self.kbqa_name = kbqa_name
        self.kbqa_version = kbqa_version
        self.dataset = dataset  # maybe move to extra class
        self.sub_experiments = sub_experiments


class SubExperiment:
    """Results of a GERBIL sub experiment."""

    def __init__(self, experiment_type: str, experiment_data: "ExperimentData") -> None:
        """Store results of a GERBIL sub experiment.

        Parameters
        ----------
        experiment_type : str
            The type of sub experiment performed
        experiment_data : ExperimentData
            The results of the sub experiment performed
        """
        self.experiment_type = experiment_type
        self.experiment_data = experiment_data


class ExperimentData:
    """Results of a Sub Experiment."""

    def __init__(
        self,
        micro_f1: float,
        micro_precision: float,
        micro_recall: float,
        macro_f1: float,
        macro_precision: float,
        macro_recall: float,
        error_count: int,
        avg_millis_per_doc: float,
        macro_f1_qald: float,
    ) -> None:
        """Store results of a Sub Experiment.

        Parameters
        ----------
        micro_f1 : float
            The Micro F1 score
        micro_precision : float
            The Micro Precision score
        micro_recall : float
            The Micro Recall score
        macro_f1 : float
            The Macro F1 score
        macro_precision : float
            The Macro Precision score
        macro_recall : float
            The Macro Recall score
        error_count : int
            The Error count
        avg_millis_per_doc : float
            The Average Milliseconds per Document (only available for the whole experiment)
        macro_f1_qald : float
            The Macro F1 score for QALD  (only available for the whole experiment)
        """
        self.micro_f1 = micro_f1
        self.micro_precision = micro_precision
        self.micro_recall = micro_recall
        self.macro_f1 = macro_f1
        self.macro_precision = macro_precision
        self.macro_recall = macro_recall
        self.error_count = error_count
        self.avg_millis_per_doc = avg_millis_per_doc
        self.macro_f1_qald = macro_f1_qald


def convert_experiment(
    gerbil_file_path: str,
    gerbil_id: int,
    gerbil_url: str,
    kbqa_name: str,
    kbqa_version: str,
) -> Experiment:
    """Read the GERBIL results from the given CSV file into a GERBIL py:class:: Experiment.

    Parameters
    ----------
    gerbil_file_path : str
        Path to the CSV file of a GERBIL experiment
    gerbil_id : int
        ID of the GERBIL experiment
    gerbil_url : str
        Base URL of the used GERBIL system
    kbqa_name : str
        Name of the evaluated KBQA system
    kbqa_version : str
        Version of the evaluated KBQA system

    Returns
    -------
    Experiment
        All data of the given GERBIL experiment
    """
    gerbil_data = pd.read_csv(
        gerbil_file_path,
        header=0,
        names=[
            "system",
            "dataset",
            "language",
            "experiment",
            "micro_f1",
            "micro_precision",
            "micro_recall",
            "macro_f1",
            "macro_precision",
            "macro_recall",
            "error_count",
            "avg_millis_per_doc",
            "macro_f1_qald",
            "timestamp",
            "gerbil_version",
        ],
    )
    sub_experiments = list()

    for index, row in gerbil_data.iterrows():
        experiment_data = ExperimentData(
            row["micro_f1"],
            row["micro_precision"],
            row["micro_recall"],
            row["macro_f1"],
            row["macro_precision"],
            row["macro_recall"],
            row["error_count"],
            row["avg_millis_per_doc"],
            row["macro_f1_qald"],
        )
        sub_experiment = SubExperiment(row["experiment"], experiment_data)
        sub_experiments.append(sub_experiment)

    experiment = Experiment(
        gerbil_id,
        gerbil_url,
        gerbil_data.iloc[0]["timestamp"],
        kbqa_name,
        kbqa_version,
        gerbil_data.iloc[0]["dataset"],
        sub_experiments,
    )

    return experiment


def save_experiment(experiment: List[Experiment], file_path: str):
    """Save the given GERBIL experiment as a JSON file.

    Parameters
    ----------
    experiment : List[Experiment]
        The GERBIL experiment
    file_path : str
        Path to a JSON file
    """
    with open(file_path, "w", encoding="utf-8") as f:
        simplejson.dump(experiment, f, default=vars, ignore_nan=True)


def summarize_results(approach: Approach) -> None:
    """Summarize all experiments made to a JSON file of the given Approach.

    Parameters
    ----------
    approach : app.main.Approach
        Selected Approach
    """
    experiments = list()

    for path, _, files in os.walk(f"/evaluation/{approach.name}"):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(path, file)
                commit_id, gerbil_id = file.split(".")[0].split("-")

                data = convert_experiment(
                    file_path, gerbil_id, "gerbil url", approach.name, commit_id
                )
                experiments.append(data)

    save_experiment(experiments, f"summary-{approach.name}.json")
