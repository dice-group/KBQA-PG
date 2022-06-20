"""Wrapper class for the BERT_TRIPLEBERT_SPBERT pipeline."""
from types import SimpleNamespace

from app.base_pipeline import BasePipeline
from app.bert_triplebert_spbert.triplebert.run import init
from app.bert_triplebert_spbert.triplebert.run import run
from app.postprocessing import postprocess_prediction
from app.preprocessing import preprocessing_qtq
from app.preprocessing import seperate_qtq


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

        init(self.arguments)  # used to make the linters work, can be removed

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
        seperate_qtq()
        preprocessing_qtq()
        run(self.arguments)

        query_pairs = postprocess_prediction()
        query = query_pairs["0"]

        return query
