"""Generator to generate a (question, sparql, triples) dataset using summarizers."""
from dataset import Dataset
from nes import NES
from summarizer import Summarizer


def generate_triples(dataset: Dataset, summarizer: Summarizer) -> None:
    """Generate triples for the dataset using the given summarizer.

    Parameters
    ----------
    dataset : Dataset
        Dataset with questions
    summarizer : Summarizer
        Used summarizer for triple generation
    """
    for question in dataset.questions:
        triple = summarizer.summarize(question.text)
        question.triples.extend(triple)


qald = Dataset()
qald.load_qald_dataset("KBQA/data-generator/qald-9-train-multilingual.json")
nes = NES()
generate_triples(qald, nes)
qald.save_qtq_dataset("KBQA/data-generator/qtq-9-train-multilingual.json")
