"""Generic summarizer."""
from abc import ABC
from abc import abstractmethod


class Summarizer(ABC):
    """Abstract summarizer."""

    @abstractmethod
    def summarize(self, question: str) -> list[str]:
        """Summarize a natural question and return relevant triples.

        Parameters
        ----------
        question : str
            A natural language question

        Returns
        -------
        list[str]
            A list of triples found by the summarizer in the format "<s> <p> <o>"
        """
