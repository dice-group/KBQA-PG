"""Wrapper class for the BERT_SPBERT_SPBERT pipeline."""
from types import SimpleNamespace

from app.base_pipeline import BasePipeline
from app.bert_spbert_spbert.spbert.run import init
from app.bert_spbert_spbert.spbert.run import run
from app.postprocessing import postprocess_prediction


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
        """Predict a SPARQL query for a given question using BERT_SPBERT_SPBERT.

        Parameters
        ----------
        question : str
            Natural language question.

        Returns
        -------
        str
            Predicted SPARQL query for the question from BERT_SPBERT_SPBERT.
        """
        run(self.arguments)

        query_pairs = postprocess_prediction()
        query = query_pairs["0"]

        return query
