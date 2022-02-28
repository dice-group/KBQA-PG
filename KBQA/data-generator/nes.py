"""NES summarizer."""

from typing import List

import nes_ner_hop
from summarizer import Summarizer


class NES(Summarizer):
    """NES summarizer from module NES_NER_Hop using dbpedia spotlight."""

    def summarize(self, question: str) -> List[str]:
        """Summarize a natural question and return found triples from dbpedia.

        Parameters
        ----------
        question : str
            A natural language Question

        Returns
        -------
        list[str]
            A list of triples found by the summarizer in the format "<s> <p> <o>"
        """
        graph = nes_ner_hop.nes_ner_hop(question)
        triples = list()

        for sub, pre, obj in graph:
            triples.append(f"<{sub}> <{pre}> <{obj}>")

        return triples
