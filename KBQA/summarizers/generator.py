"""Generator to generate a (question, sparql, triples) dataset using summarizers."""
import argparse

from data_generator.dataset import Dataset
from data_generator.summarizer import Summarizer
from one_hop_rank_summarizer import OneHopRankSummarizer


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
        print(question.text)
        triple = summarizer.summarize(question.text)
        question.triples.extend(triple)


if __name__ == "__main__":
    # qald = Dataset()
    # qald.load_qald_dataset("KBQA/data-generator/qald-9-train-multilingual.json")
    # nes = NES()
    # generate_triples(qald, nes)
    # qald.save_qtq_dataset("KBQA/data-generator/qtq-9-train-multilingual.json")

    DATASET = "datasets/qald-9-train-multilingual.json"

    train_data = Dataset()
    train_data.load_dataset(DATASET)
    ohrs = OneHopRankSummarizer(dataset_path=DATASET)

    parser = argparse.ArgumentParser()
    parser.add_argument("question", type=str, help="Natural language question")

    args = parser.parse_args()

    # ohrs.summarize(args.question)
    generate_triples(train_data, ohrs)
    train_data.save_qtq_dataset("qtq_qald_9.json")
