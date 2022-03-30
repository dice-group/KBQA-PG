"""Generic summarizer."""
from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Tuple

from KBQA.appB.data_generator import Question


class BaseSummarizer(ABC):
    """Abstract summarizer."""

    @abstractmethod
    def summarize(self, question: Question) -> List[str]:
        """Summarize a natural question and return relevant triples.

        Parameters
        ----------
        question : Question
            Question object containing a natural language question.

        Returns
        -------
        list[str]
            A list of triples found by the summarizer in the format "<s> <p> <o>"
        """


class ExtendedSummarizer(ABC):
    """Summarizer to extend the BaseSummarizer.

        Extended abstract summarizer class, which is used to
    provide a summarize function, which returns the ranks and
    confidence score for each triple.
    """

    @abstractmethod
    def summarize_ranks_confidence(
        self, question: Question
    ) -> List[Tuple[str, float, float]]:
        """Summarize triples with ranks and confidence scores.

        Summarize a natural language question and return relevant
        triples, their rank and their confidence score.

        Parameters
        ----------
        question : Question
            Question object containing a natural language question.

        Returns
        -------
        list[((URIRef, URIRef, URIRef), float, float)]
            List of summarized triples and their ranks and confidence.
        """
