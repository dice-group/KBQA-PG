"""Generator to generate a (question, sparql, triples) dataset using summarizers."""
import pickle
from typing import Union
from typing import Tuple

from KBQA.appB.data_generator.dataset import Dataset
from KBQA.appB.data_generator.dataset import Question
from KBQA.appB.summarizers.NES_NER_Hop.nes_summarizer import NES
from KBQA.appB.summarizers.from_answer_summarizer.from_answer_summarizer import (
    FromAnswerSummarizer,
)
from KBQA.appB.summarizers.one_hop_rank_summarizer.one_hop_rank_summarizer import (
    OneHopRankSummarizer,
)
from KBQA.appB.summarizers.base_summarizer.summarizer import Summarizer


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
                triple = summarizer.summarize(question)
                question.triples = triple
                print(f"Found {len(triple)} triples!")
                self.current_question += 1
            # question.save_to_qtq_dataset("KBQA/data-generator/qtq-9-train-multilingual-2.json")
            except Exception as exception:  # pylint: disable=broad-except
                print(f"Error summarizing question {question.text}: {exception}")


def get_args() -> Tuple[str, str, str]:
    """Get cmd-args.

    :return:
        dataset_name: Name of the a QALD or LC-QuAD dataset located at ROOT_PATH
        summarizer_name: Name of a summarizer such as NES, FromAnswer or OneHopRanking
        outfile_name: Name of the output qtq file.
    :rType: tuple
    """
    (opt_args, _) = getopt.getopt(
        sys.argv[1:], "d:s:o", ["dataset=", "summarizer=", "output="]
    )
    dataset_name = ""
    summarizer_name = "NES"
    outfile_name = ""
    for opt, value in opt_args:
        if opt in ("-d", "--dataset"):
            dataset_name = value
        if opt in ("-s", "--summarizer"):
            summarizer_name = value
        if opt in ("-o", "--output"):
            outfile_name = value
    return dataset_name, summarizer_name, outfile_name


def main() -> None:
    """Start this module from as __main__ (e.g. from commandline) to invoke this function.

    Synopsis: python generator.py {--dataset | -d} <dataset-name> [{--summarizer | -s} <summarizer>] [{--output|-o} <output-file>]
    """
    # Gather the given options.
    dataset_name, summarizer_name, outfile_name = get_args()

    if dataset_name == "":
        print(
            f'Provide a dataset with "{sys.argv[0]}\\ {{-d | --dataset}} <dataset_name>".'
        )
        sys.exit()

    summarizers = {
        "NES": NES,
        "FromAnswer": FromAnswerSummarizer,
        "OneHopRanking": OneHopRankSummarizer,
    }

    if summarizer_name not in summarizers:
        print(
            f'Provide a summarizer with "{sys.argv[0]}\\ {{-s | --summarizer}} <summarizer_name>".'
        )
        print("Available Summarizers are:")
        for summ in summarizers:
            print(summ)
    else:
        summarizer = summarizers[summarizer_name]()

    if outfile_name == "":
        print("[WARNING] output file not specified, defaulting to:", end=" ")
        outfile_name = "qtq-" + dataset_name
        print(outfile_name)
        print(
            f'Provide a output file name with "{sys.argv[0]}\\ {{-o | --output}} <outfile_name>".'
        )

    DATASET_ROOT_PATH = "./../../datasets"
    dataset = Dataset()
    dataset.load_dataset(DATASET_ROOT_PATH + "/" + dataset_name)

    dataset_generator = DatasetGenerator(dataset)

    try:
        with open("generator.pickle", "rb") as f:
            dataset_generator = pickle.load(f)
        print("Continue with latest run.")
    except FileNotFoundError:
        pass

    try:
        dataset_generator.generate_triples(summarizer)
    except KeyboardInterrupt:
        print("Interrupted summarization. Save progress...")
        with open("generator.pickle", "wb") as f:
            pickle.dump(dataset_generator, f)
    finally:
        dataset_generator.dataset.save_qtq_dataset(
            DATASET_ROOT_PATH + "/" + outfile_name
        )

    sys.exit()


# Call from shell as main.
if __name__ == "__main__":
    import sys
    import getopt

    main()
