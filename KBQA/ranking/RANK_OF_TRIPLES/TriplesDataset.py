"""Function get triples from dataset."""
import json
from typing import List


def getTriplesDataset(inputQuestion: str, jsonfile: str) -> List[str]:
    """
    Given question and dataset with questions triples. Triples for the given question are returned.

    --------------
    :param inputQuestion: question string.
    :param jsonfile: path string to json file.
    :return: list with triples as string.
    """
    with open(jsonfile, encoding="utf8") as file:
        data_js = json.load(file)
    questionTriples = list()
    # parse all triples from the json for one question
    for questionDataset in data_js["questions"]:
        if questionDataset["question"] == inputQuestion:
            questionTriples = questionDataset["triples"]
    return questionTriples


def main() -> None:
    """Call getTriplesDataset("Your question", file)."""
    # file = "C:/Users/User/Downloads/qald8-test-golden.qtq.json"
    # list = getTriplesDataset("Bla", file)
    # print(list)


if __name__ == "__main__":
    # start_time = time.time()
    main()
    # print(time.time() - start_time)
