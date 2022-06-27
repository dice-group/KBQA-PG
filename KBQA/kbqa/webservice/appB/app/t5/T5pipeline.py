"""Wrapper class for the t5 pipeline."""
from types import SimpleNamespace

from app.base_pipeline import BasePipeline
from app.t5.predict import run
from app.t5.predict import init
from app.postprocessing import postprocess_prediction
from app.preprocessing import preprocessing_qtq
from app.preprocessing import seperate_qtq


class t5Pipeline(BasePipeline):
    """Pipeline for the t5 architecture."""

    def __init__(self, arguments: SimpleNamespace) -> None:
        """Initialize pipeline for the t5 architecture.

        Parameters
        ----------
        arguments : SimpleNamespace
            Namespace containing all parameters/arguments for running
            SPBERT.
        """
        super().__init__(arguments)
        init(self.arguments)

    def predict_sparql_query(self, question: str) -> str:
        """Predict a SPARQL query for a given question using t5.

        Parameters
        ----------
        question : str
            Natural language question.

        Returns
        -------
        str
            Predicted SPARQL query for the question from t5.
        """
        seperate_qtq()
        preprocessing_qtq()
        run(self.arguments)

        query_pairs = postprocess_prediction()
        query = query_pairs["0"]

        return query