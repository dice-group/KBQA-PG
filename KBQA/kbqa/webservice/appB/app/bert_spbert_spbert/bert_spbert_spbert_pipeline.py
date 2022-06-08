"""Wrapper class for the BERT_SPBERT_SPBERT pipeline."""
from types import SimpleNamespace

from app.base_pipeline import BasePipeline
from app.bert_spbert_spbert.bert_wordpiece_spbert.run import init
from app.bert_spbert_spbert.bert_wordpiece_spbert.run import run
from app.bert_spbert_spbert.postprocessing import postprocessing


class BertSPBertSPBertPipeline(BasePipeline):
    """Pipeline for the BERT_SPBERT_SPBERT architecture."""

    def __init__(self, arguments: SimpleNamespace) -> None:
        """Initialize pipeline for the BERT_SPBERT_SPBERT architecture.

        Parameters
        ----------
        arguments : SimpleNamespace
            Namespace containing all parameters/arguments for running
            SPBERT.
        """
        super().__init__(arguments)

        init(self.arguments)

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
        run(self.arguments)

        query_pairs = postprocessing()
        query = query_pairs["0"]

        return query
