"""Base class for all architectures.

Abstract class for all architectures. An Archicture should extend this
class and implement the pipeline for predicting a sparql query.
"""
from abc import ABC
from abc import abstractmethod
from types import SimpleNamespace


class BasePipeline(ABC):
    """Initialize a pipeline, which is used to predict a SPARQL query."""

    @abstractmethod
    def __init__(self, arguments: SimpleNamespace) -> None:
        """Constuctor. The arguments are supposed to be stored in a namespace.

        Parameters
        ----------
        argmuents : SimpleNamespace
            Namespace, which contains all arguments for running
            the pipeline.
        """
        self.arguments = arguments

    @abstractmethod
    def predict_sparql_query(self, question: str) -> str:
        """Predict a SPARQL query using the pipeline for the architecture.

        Override this function to implement the pipeline for the architecture.

        Parameters
        ----------
        question : str
            Natural language question.

        Returns
        -------
        str
            Predicted SPARQL query.
        """
