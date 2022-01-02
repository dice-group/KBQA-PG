from abc import ABC
from abc import abstractmethod


class Summarizer(ABC):
    @abstractmethod
    def summarize(self, question: str):
        pass
