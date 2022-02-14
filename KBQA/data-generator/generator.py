"""Generator to generate a (question, sparql, triples) dataset using summarizers."""
import pickle
from typing import Union

from dataset import Dataset
from dataset import Question
from nes import NES
from summarizer import Summarizer


class DatasetGenerator:
    """Generate a dataset with the help of a summarizer."""

    def __init__(self, input_dataset: Dataset) -> None:
        """Initialize the dataset generator.

        :param input_dataset: The used dataset
        :type input_dataset: Dataset
        """
        self.dataset = input_dataset
        self.current_question = 0

    def next_question(self) -> Union[Question, None]:
        """Get the next question for summarization.

        :return: The next question or None
        :rtype: Question
        """
        self.current_question += 1

        if self.current_question >= len(self.dataset.questions):
            return None

        return self.dataset.questions[self.current_question]
        # for position, question in enumerate(self.input_dataset.questions):
        #     self.current_question = position
        #     yield question

    def generate_triples(self, summarizer: Summarizer) -> None:
        """Generate triples for the dataset using the given summarizer.

        Parameters
        ----------
        summarizer : Summarizer
            Used summarizer for triple generation
        """
        while True:
            question = self.next_question()

            if question is None:
                break

            try:
                print(f"Summarize question '{question.text}'")
                triple = summarizer.summarize(question.text)
                question.triples.extend(triple)
                print(f"Found {len(triple)} triples!")
                # question.save_to_qtq_dataset("KBQA/data-generator/qtq-9-train-multilingual-2.json")
            except Exception as exception:  # pylint: disable=broad-except
                print(f"Error summarizing question {question.text}: {exception}")


qald = Dataset()
qald.load_qald_dataset("KBQA/data-generator/qald-9-train-multilingual.json")
nes = NES()

dataset_generator = DatasetGenerator(qald)

try:
    with open("generator.pickle", "rb") as f:
        dataset_generator = pickle.load(f)
    print("Continue with latest run.")
except FileNotFoundError:
    pass

try:
    dataset_generator.generate_triples(nes)
except KeyboardInterrupt:
    print("Interrupted summarization. Save progress...")
    with open("generator.pickle", "wb") as f:
        pickle.dump(dataset_generator, f)
finally:
    dataset_generator.dataset.save_qtq_dataset(
        "KBQA/data-generator/qtq-9-train-multilingual.json"
    )
