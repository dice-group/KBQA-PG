"""Wrapper class for the KNOWBERT_SPBERT_SPBERT pipeline."""
from types import SimpleNamespace

from app.base_pipeline import BasePipeline
from app.knowbert_spbert_spbert.kb.run import init
from app.knowbert_spbert_spbert.kb.run import predict
from app.knowbert_spbert_spbert.kb.run import test
from app.knowbert_spbert_spbert.kb.run import train
from app.postprocessing import postprocess_prediction
from app.preprocessing import preprocessing_qtq
from app.preprocessing import seperate_qtq


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
        self.model, self.batcher, self.tokenizer, self.device = init(arguments)

    def train_pipeline(self) -> None:
        """Wrap train function from run.py."""
        train(self.model, self.batcher, self.tokenizer, self.device, self.arguments)

    def test_pipeline(self) -> None:
        """Wrap test function from run.py."""
        test(self.model, self.batcher, self.tokenizer, self.device, self.arguments)

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
        seperate_qtq()
        preprocessing_qtq()

        predict(self.model, self.batcher, self.tokenizer, self.device, self.arguments)

        query_pairs = postprocess_prediction()
        query = query_pairs["0"]

        return query
