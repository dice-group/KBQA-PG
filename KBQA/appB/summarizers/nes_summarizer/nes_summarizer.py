"""NES summarizer."""
from typing import List

from KBQA.appB.data_generator import Question
from KBQA.appB.summarizers import BaseSummarizer

from .nes_ner_hop import nes_ner_hop


class NES(BaseSummarizer):
    """NES summarizer from module nes_summarizer using dbpedia spotlight."""

    def summarize(self, question: Question) -> List[str]:
        """Summarize a natural question and return found triples from dbpedia.

        Parameters
        ----------
        question : Question
            A Question object containing a natural language question

        Returns
        -------
        list[str]
            A list of triples found by the summarizer in the format "<s> <p> <o>"
        """
        print(question)
        graph = nes_ner_hop(question.text)
        triples = list()

        for sub, pre, obj in graph:
            triples.append(f"<{sub}> <{pre}> <{obj}>")

        return triples
