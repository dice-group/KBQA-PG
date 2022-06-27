"""Implementation for the gold summarizer."""
import json
import os
from typing import List

from app.summarizer import BaseSummarizer


class GoldSummarizer(BaseSummarizer):
    """Gold summarizer, which returns only the triples, which are answering a question.

    Parameters
    ----------
    dataset : str
        Name of the gold dataset. Only 'qald8' and 'qald9' are supported.
    verbose : bool, optional
        Print some statements (default: True).

    Raises
    ------
    ValueError
        If dataset is not 'qald8' or 'qald9'.
    """

    def __init__(self, dataset: str, verbose: bool = True) -> None:
        if dataset == "qald8":
            self.dataset = "qald8-test-golden.qtq.json"
        elif dataset == "qald9":
            self.dataset = "qald9-test-golden.qtq.json"
        else:
            raise ValueError("Only 'qald8' and 'qald9' are supported as dataset.")

        self.verbose = verbose

    def summarize(self, question: str) -> List[str]:
        """Summarize the subgraph with triples containing the answers.

        Parameters
        ----------
        question : Question
            Question object containing the question to summarize.

        Returns
        -------
        list[str]
            List containing the triples in the format <subj> <pred> <obj>.
        """
        dataset = os.path.join(os.path.dirname(__file__), f"datasets/{self.dataset}")

        with open(dataset, "r", encoding="utf-8") as file:
            content = json.load(file)

        for question_obj in content["questions"]:
            if question_obj["question"] == question:
                return question_obj["triples"]

        if self.verbose:
            print(
                f"WARNING: Question '{question}' was not found in the gold dataset. No triples are returned."
            )

        return list()
