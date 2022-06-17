"""Wrapper class for the KNOWBERT_SPBERT_SPBERT pipeline."""
from types import SimpleNamespace

from app.base_pipeline import BasePipeline


class KnowBertSPBertSPBertPipeline(BasePipeline):
    """Pipeline for the KNOWBERT_SPBERT_SPBERT architecture."""

    def __init__(self, arguments: SimpleNamespace) -> None:
        """Initialize pipeline for the KNOWBERT_SPBERT_SPBERT architecture.

        Parameters
        ----------
        arguments : SimpleNamespace
            Namespace containing all parameters/arguments for running
            SPBERT.
        """
        super().__init__(arguments)

        # TODO add initialization of KnowBert
        print(arguments)  # used to make the linters work, can be removed

    def predict_sparql_query(self, question: str) -> str:
        """Precit a SPARQL query for a given question.

        Parameters
        ----------
        question : str
            Natural language question.

        Returns
        -------
        str
            Predicted SPARQL query for the question.
        """
        # TODO add prediction of KnowBert
        return ""
