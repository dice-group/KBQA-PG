"""Wrapper class for the BERT_SPBERT pipeline."""
from types import SimpleNamespace

from app.base_pipeline import BasePipeline
from app.bert_spbert.spbert.run import init
from app.bert_spbert.spbert.run import run
from app.postprocessing import postprocess_prediction
from app.preprocessing import preprocessing_qtq
from app.preprocessing import seperate_qtq


class BertSPBertPipeline(BasePipeline):
    """Pipeline for the BERT_SPBERT architecture."""

    def __init__(self, arguments: SimpleNamespace) -> None:
        """Initialize pipeline for the BERT_SPBERT architecture.

        Parameters
        ----------
        arguments : SimpleNamespace
            Namespace containing all parameters/arguments for running
            SPBERT.
        """
        super().__init__(arguments)

        init(self.arguments)

    def predict_sparql_query(self, question: str) -> str:
        """Predict a SPARQL query for a given question using BERT_SPBERT.

        Parameters
        ----------
        question : str
            Natural language question.

        Returns
        -------
        str
            Predicted SPARQL query for the question from BERT_SPBERT.
        """
        seperate_qtq()
        preprocessing_qtq()

        run(self.arguments)

        query_pairs = postprocess_prediction()
        query = query_pairs["0"]

        return query
