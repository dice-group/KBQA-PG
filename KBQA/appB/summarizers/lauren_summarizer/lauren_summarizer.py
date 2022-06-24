"""Summarizer, which uses LAUREN to find triples."""
from typing import Dict
from typing import List
from typing import Union

from KBQA.appB.data_generator import Question
from KBQA.appB.summarizers import BaseSummarizer
import requests


class LaurenSummarizer(BaseSummarizer):
    """Summarizer based on LAUREN (https://github.com/dice-group/LAUREN).

    This summarizer is a wrapper for LAUREN and returns the found triples.

    Parameters
    ----------
    limit : int, optional
        Maximum number of triples (default: 100).

    Raises
    ------
    ValueError
        If the number of triples is less than 0.

    """

    def __init__(self, limit: int = 100) -> None:
        self.limit = limit

        if limit < 0:
            raise ValueError("Limit should be greater than 0.")

    def summarize(self, question: Question) -> List[str]:
        """Summarize a subgraph for a given question.

        Parameters
        ----------
        question : Question
            Question object containing the asked question to summarize.

        Returns
        -------
        list[str]
            List of triples in the format <subject> <predicate> <object>.
        """
        data: Dict[str, Union[str, int]] = dict()

        data["question"] = question.text
        data["size"] = self.limit

        response = requests.get(
            "http://qa-collab.cs.upb.de:5000/get-triples-by-text", json=data
        ).json()

        triples = list()

        for triple in response["triples"]:
            subj = triple["subject"]
            pred = triple["predicate"]
            obj = triple["object"]

            formated_triple = f"<{subj}> <{pred}> <{obj}>"

            triples.append(formated_triple)

        return triples
