"""Class to store a QTQL dataset, when generating it."""
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Union


class Question:
    """A question object in a QTQL dataset.

    Parameters
    ----------
    question : str
        Natural language question.
    sparql : str
        SPARQL query.
    triples : list
        List of triples for the question (found by a summarizer).
    labels : list
        List of corresponding labels for the triples.
    """

    def __init__(
        self,
        question: str,
        sparql: str,
        triples: List[str],
        labels: Union[List[str], None] = None,
    ) -> None:
        if labels is None:
            labels = list()

        self.text = question
        self.sparql = sparql
        self.triples = triples
        self.labels = labels


class QTQLDataset:
    """Class for QTQL dataset."""

    def __init__(self) -> None:
        self.questions: List[Question] = list()

    def load_qtq_dataset(self, path: str) -> None:
        """Load a QTQ dataset, for which the QTQL dataset should be built.

        Parameters
        ----------
        path : str
            Path to QTQ dataset.
        """
        with open(path, encoding="utf-8") as file_handle:
            qtq_data = json.load(file_handle)

        questions = qtq_data["questions"]

        for question in questions:
            text = question["question"]
            query = question["query"]
            triples = question["triples"]

            self.questions.append(Question(text, query, triples))

    def save_qtql_dataset(self, path: str) -> None:
        """Save the dataset.

        Parameters
        ----------
        path : str
            Path to the place, where the QTQL dataset should be stored.
        """
        dataset: Dict[str, List] = {"questions": list()}

        for question in self.questions:
            qtql: Dict[str, Any] = dict()
            qtql["question"] = question.text
            qtql["query"] = question.sparql
            qtql["triples"] = question.triples
            qtql["labels"] = question.labels
            dataset["questions"].append(qtql)

        with open(path, "w+", encoding="utf-8") as file_handle:
            json.dump(dataset, file_handle, indent=4, separators=(",", ": "))
