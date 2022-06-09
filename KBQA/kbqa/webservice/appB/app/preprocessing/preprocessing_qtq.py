"""Preprocess a seperated QTQ dataset to prepare it for the use of SPBert."""
import os
import re
from typing import List

from app.arguments.args_preprocessing import PREPROCESSING_QTQ
from app.bert_wordpiece_spbert.generator_utils import encode
from app.bert_wordpiece_spbert.generator_utils import SPARQL_KEYWORDS


def preprocess_sentence(words: str) -> str:
    """Preprocess a single sentence from an en file.

    Parameters
    ----------
    words : str
        Natural language sentence.

    Returns
    -------
    words : str
        Preprocessed natural language sentence.
    """
    # creating a space between a word and the punctuation following it
    # eg: "he is a boy." => "he is a boy ."
    # Reference:- https://stackoverflow.com/questions/3645931/python-padding-punctuation-with-white-spaces-keeping-punctuation
    words = re.sub(r"([?.!,¿])", r" \1 ", words)
    words = re.sub(r'[" "]+', " ", words)

    # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
    # w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)
    # w = re.sub(r'\[.*?\]', '<ans>', w).rstrip().strip()
    words = words.rstrip().strip().lower()

    # adding a start and an end token to the sentence
    # so that the model know when to start and stop predicting.
    # w = '<start> ' + w + ' <end>'
    return words


def preprocess_sparql(sparql: str) -> str:
    """Preprocess a sparql-query from a sparql file.

    Parameters
    ----------
    sparql : str
        SPARQL-query.

    Returns
    -------
        Preprocessed SPARQL-query.
    """
    for pre_name, pre_url in re.findall(r"PREFIX\s([^:]*):\s<([^>]+)>", sparql):
        sparql = re.sub(f"\\b{pre_name}:([^\\s]+)", f"<{pre_url}\\1>", sparql)
    # Remove prefixes
    sparql = re.sub(r"PREFIX\s[^\s]*\s[^\s]*", "", sparql)

    # replace sing quote to double quote
    sparql = re.sub(r"(\B')", '"', sparql)
    sparql = re.sub(r"'([^_A-Za-z])", r'"\1', sparql)

    # remove timezone 0
    sparql = re.sub(r"(\d{4}-\d{2}-\d{2})T00:00:00Z", r"\1", sparql)

    sparql = encode(sparql.rstrip().strip())

    normalize_s = []
    for token in sparql.split():
        beginning_subtoken = re.search(r"^\w+", token)

        if beginning_subtoken is not None:
            beg_subtoken = beginning_subtoken.group()

            if str(beg_subtoken).upper() in SPARQL_KEYWORDS:
                token = re.sub(r"^\w+", str(beg_subtoken).lower(), token)

        normalize_s.append(token)

    sparql = " ".join(normalize_s)

    sparql = " ".join(sparql.split())

    return sparql


def preprocess_triples(triples: List[str]) -> List[str]:
    """Preprocess a list of triples from a triple file.

    Parameters
    ----------
    triples : list
        List of tripels from a triples file.

    Returns
    -------
    triples : list
        Preprocessed triples.
    """
    return [preprocess_sparql(triple) for triple in triples]


def preprocessing_qtq() -> None:
    """Preprocess a QTQ dataset splitted into an en, sparql and triples file."""
    args = PREPROCESSING_QTQ

    data_dir = args.data_dir
    subset = args.subset
    output_dir = args.output_dir

    data_dir = data_dir.rstrip("/")
    output_dir = output_dir.rstrip("/")

    # create output directory to store output files for SPBERT
    if os.path.exists(output_dir) is False:
        os.makedirs(output_dir)

    with open(f"{output_dir}/{subset}.en", "w", encoding="utf-8") as out:
        with open(f"{data_dir}/{subset}.en", encoding="utf-8") as file:
            for line in file:
                if "\n" == line[-1]:
                    line = line[:-1]
                out.write(preprocess_sentence(line))
                out.write("\n")

    with open(f"{output_dir}/{subset}.sparql", "w", encoding="utf-8") as out:
        with open(f"{data_dir}/{subset}.sparql", encoding="utf-8") as file:
            for line in file:
                if "\n" == line[-1]:
                    line = line[:-1]
                out.write(preprocess_sparql(line))
                out.write("\n")

    with open(f"{output_dir}/{subset}.triple", "w", encoding="utf-8") as out:
        with open(f"{data_dir}/{subset}.triple", encoding="utf-8") as file:
            for line in file:
                if "\n" == line[-1]:
                    line = line[:-1]
                triples = line.split("\t")
                out.write("\t".join(preprocess_triples(triples)))
                out.write("\n")


if __name__ == "__main__":
    preprocessing_qtq()
