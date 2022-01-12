"""Question Dataset."""
import json
import re
from typing import Dict
from typing import List


class Question:
    """A Question in a :py:class:Dataset."""

    def __init__(
        self,
        question: str,
        sparql: str = "",
        answers: List = list(),
        triples: List = list(),
    ) -> None:
        """Initialize a Question.

        Parameters
        ----------
        question : str
            The natural language question
        sparql : str, optional
            The gold SPARQL query. Defaults to "", by default ""
        answers : List, optional
            A List of answers to the question, by default list()
        triples : List, optional
            A List related triples to the question, by default list()
        """
        self.text = question
        self.sparql: str = sparql
        self.answers: List = answers
        self.triples: List = triples


class Dataset:
    """Represents a question dataset."""

    def __init__(self, language: str = "en") -> None:
        """Initialize a question Dataset.

        Parameters
        ----------
        language : str, optional
            Default language of the dataset, by default "en"
        """
        self.language: str = language
        self.questions: List[Question] = list()

    def load_dataset(self, dataset_path: str) -> None:
        """Load datset from given path.

        Currently supported are QALD and LC-QuAD

        Parameters
        ----------
        dataset_path : str
            Path to dataset file

        :raises ValueError: If dataset is not recognized as QALD or LC-QuAD
        """
        qald_regex = r"qald-[0-9]+-(train|test)-multilingual"
        lc_quad_regex = r"lc-quad-(train|test)"
        dataset_file = dataset_path.split("/")[-1]

        if re.match(qald_regex, dataset_file):
            self.load_qald_dataset(dataset_path)
        elif re.match(lc_quad_regex, dataset_file):
            self.load_lc_quad_dataset(dataset_path)
        else:
            raise ValueError(f"{dataset_file} is neither QALD nor LC-QuAD datset")

    def load_qald_dataset(self, dataset_path: str) -> None:
        """Load QALD dataset from given path.

        Parameters
        ----------
        dataset_path : str
            Path to QALD dataset json file
        """
        with open(dataset_path, "r", encoding="utf-8") as file_handle:
            qald_data = json.load(file_handle)

        questions = qald_data["questions"]

        for question in questions:
            for question_lang in question["question"]:
                if question_lang["language"] == self.language:
                    nl_question = question_lang["string"]
                    break

            sparql_query = question["query"]["sparql"]
            answers: List = list()
            results = question["answers"][0]["results"]

            if len(results) > 0:
                for question_results in results["bindings"]:
                    if len(question_results) > 0:
                        answers.append(list(question_results.values())[0]["value"])

            self.questions.append(Question(nl_question, sparql_query, answers))

    def load_lc_quad_dataset(self, dataset_path: str) -> None:
        """Load LC-QuAD dataset from given path.

        Parameters
        ----------
        dataset_path : str
            Path to LC-QuAD dataset json file
        """
        with open(dataset_path, "r", encoding="utf-8") as file_handle:
            qald_data = json.load(file_handle)

        for question in qald_data:
            nl_question = question["corrected_question"]
            sparql_query = question["sparql_query"]
            answers: List = list()
            self.questions.append(Question(nl_question, sparql_query, answers))

    def save_qtq_dataset(self, dataset_path: str) -> None:
        """Save QTQ dataset to disk.

        Parameters
        ----------
        dataset_path : str
            Path to QTQ dataset json file
        """
        dataset: Dict = {"questions": list()}

        for question in self.questions:
            qtq: Dict = {}
            qtq["question"] = question.text
            qtq["query"] = question.sparql
            qtq["triples"] = question.triples
            dataset["questions"].append(qtq)

        with open(dataset_path, "w", encoding="utf-8") as file_handle:
            json.dump(dataset, file_handle, indent=4, separators=(",", ": "))
