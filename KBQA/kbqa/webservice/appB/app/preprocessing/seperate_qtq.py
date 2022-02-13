"""Module to seperate a QTQ dataset into an en, sparql and triple file."""
import json
from typing import List

from app.arguments.args_preprocessing import SEPERATE_QTQ


def filter_triples(triples: List) -> List:
    """Filter out triples containing new line character.

    Parameters
    ----------
    triples : list
        List of triples.

    Returns
    -------
    filtered_triples : list
        List of filtered triples.
    """
    return [triple for triple in triples if "\n" not in triple]


def seperate_qtq() -> None:
    """Seperate a QTQ dataset into an en, sparql and triple file."""
    args = SEPERATE_QTQ

    data_dir = args.data_dir
    subset = args.subset
    output_dir = args.output_dir

    data_dir = data_dir.rstrip("/")
    output_dir = output_dir.rstrip("/")

    with open(f"{output_dir}/{subset}.en", "w", encoding="utf-8") as en_file, open(
        f"{output_dir}/{subset}.sparql", "w", encoding="utf-8"
    ) as sparql_file, open(
        f"{output_dir}/{subset}.triple", "w", encoding="utf-8"
    ) as triple_file, open(
        f"{data_dir}/{subset}.json", "r", encoding="utf-8"
    ) as data_file:

        data = json.load(data_file)

        for element in data["questions"]:
            en_file.write(element["question"] + "\n")
            sparql_file.write(element["query"] + "\n")
            triple_file.write("\t".join(filter_triples(element["triples"])) + "\n")


if __name__ == "__main__":
    seperate_qtq()
