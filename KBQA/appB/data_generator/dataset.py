"""Question Dataset."""
import json
from typing import Dict
from typing import List
from typing import Optional


class Question:
    """A Question in a :py:class:Dataset."""

    def __init__(
        self,
        question: str,
        sparql: str = "",
        answers: Optional[List] = None,
        triples: Optional[List] = None,
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
        if triples is None:
            triples = list()
        if answers is None:
            answers = list()

        self.text = question
        self.sparql: str = sparql
        self.answers: List = answers
        self.triples: List = triples

    def save_to_qtq_dataset(self, dataset_path: str) -> None:
        """Append question to QTQ dataset and save it to disk.

        Parameters
        ----------
        dataset_path : str
            Path to QTQ dataset json file
        """
        try:
            with open(dataset_path, "r", encoding="utf-8") as file_handle:
                dataset = json.load(file_handle)
        except OSError:
            dataset = {"questions": list()}

        qtq: Dict = {}
        qtq["question"] = self.text
        qtq["query"] = self.sparql
        qtq["triples"] = self.triples
        dataset["questions"].append(qtq)

        with open(dataset_path, "w", encoding="utf-8") as file_handle:
            json.dump(dataset, file_handle, indent=4, separators=(",", ": "))


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
            answers = list()
            results = question["answers"][0]["results"]

            if len(results) > 0:
                for question_results in results["bindings"]:
                    if len(question_results) > 0:
                        answers.append(list(question_results.values())[0]["value"])

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

        with open(dataset_path, "w+", encoding="utf-8") as file_handle:
            json.dump(dataset, file_handle, indent=4, separators=(",", ": "))
