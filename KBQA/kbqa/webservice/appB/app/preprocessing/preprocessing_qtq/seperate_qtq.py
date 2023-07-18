"""Module to seperate a QTQ dataset into an en, sparql and triple file."""
import json
import os
from types import SimpleNamespace
from typing import List


# path to store the qtq files
QTQ_DATA_DIR = "app/data/input"
# name of the .en, .sparql and .triple files
SPLIT_NAME = "question"

SEPERATE_QTQ = SimpleNamespace(
    **{
        # --data, dest="data_dir", required=True
        "data_dir": QTQ_DATA_DIR,
        # --subset, dest="subset", required=True
        "subset": SPLIT_NAME,
        # --output, dest="output_dir", required=True
        "output_dir": "app/data/sep",
    }
)


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
    sep_dir = output_dir.rstrip("/")

    # create sep directory to store seperated files
    if os.path.exists(sep_dir) is False:
        os.makedirs(sep_dir)

    with open(f"{sep_dir}/{subset}.en", "w", encoding="utf-8") as en_file, open(
        f"{sep_dir}/{subset}.sparql", "w", encoding="utf-8"
    ) as sparql_file, open(
        f"{sep_dir}/{subset}.triple", "w", encoding="utf-8"
    ) as triple_file, open(
        f"{data_dir}/{subset}.json", encoding="utf-8"
    ) as data_file:
        data = json.load(data_file)

        for element in data["questions"]:
            en_file.write(element["question"] + "\n")
            sparql_file.write(element["query"] + "\n")
            triple_file.write("\t".join(filter_triples(element["triples"])) + "\n")
