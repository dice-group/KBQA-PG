import json
from typing import List


class Question:
    def __init__(self, question: str, sparql: str = "", answers: List = []) -> None:
        self.text = question
        self.sparql: str = sparql
        self.answers: List = answers
        self.triples: List = []


class Dataset:
    def __init__(self, language: str = "en") -> None:
        self.language: str = language
        self.questions: List[Question] = []

    def load_dataset(self, dataset_path: str) -> dict:
        """
        Load dataset from given path.
        :param dataset_path: Path to QALD dataset
        :return: The dataset in QALD format
        """
        with open(dataset_path, "r", encoding="utf-8") as file_handle:
            qald_data = json.load(file_handle)

        questions = qald_data["questions"]

        for question in questions:
            for question_lang in question["question"]:
                if question_lang["language"] == "en":
                    nl_question = question_lang["string"]
                    break

            sparql_query = question["query"]["sparql"]

            answers = []

            for question_results in question["answers"][0]["results"]:
                if len(question_results) > 0:
                    answers.append(
                        list(question_results["bindings"].values())[0]["value"]
                    )

            self.questions.append(Question(nl_question, sparql_query, answers))
