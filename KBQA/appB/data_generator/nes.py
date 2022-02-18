"""NES summarizer."""
from typing import List

from KBQA.appB.summarizers.NES_NER_Hop.nes_ner_hop import nes_ner_hop
from KBQA.appB.data_generator.summarizer import Summarizer


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
        graph = nes_ner_hop(question)
        triples = list()

        for sub, pre, obj in graph:
            triples.append(f"<{sub}> <{pre}> <{obj}>")

        return triples
