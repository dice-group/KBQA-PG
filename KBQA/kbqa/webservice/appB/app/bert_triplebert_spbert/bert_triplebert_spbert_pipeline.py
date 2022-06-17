"""Wrapper class for the BERT_TRIPLEBERT_SPBERT pipeline."""
from types import SimpleNamespace

from app.base_pipeline import BasePipeline


class BertTripleBertSPBertPipeline(BasePipeline):
    """Pipeline for the BERT_TRIPLEBERT_SPBERT architecture."""

    def __init__(self, arguments: SimpleNamespace) -> None:
        """Initialize pipeline for the BERT_TRIPLEBERT_SPBERT architecture.

        Parameters
        ----------
        arguments : SimpleNamespace
            Namespace containing all parameters/arguments for running
            SPBERT.
        """
        super().__init__(arguments)

        # TODO add initialization of TripleBert
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
        # TODO add prediction of TripleBert
        return ""
