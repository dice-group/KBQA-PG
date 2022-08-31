"""Generic summarizer."""
from abc import ABC
from abc import abstractmethod
from typing import List

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
