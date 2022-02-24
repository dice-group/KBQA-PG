"""NES summarizer."""
from typing import List

from KBQA.appB.summarizers.NES_NER_Hop.nes_ner_hop import nes_ner_hop
from KBQA.appB.summarizers.base_summarizer.summarizer import Summarizer
from KBQA.appB.data_generator.dataset import Question


class NES(Summarizer):
    """NES summarizer from module NES_NER_Hop using dbpedia spotlight."""

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
