import argparse
import re

from generator_utils import encode
from generator_utils import SPARQL_KEYWORDS


def preprocess_sentence(w):
    # creating a space between a word and the punctuation following it
    # eg: "he is a boy." => "he is a boy ."
    # Reference:- https://stackoverflow.com/questions/3645931/python-padding-punctuation-with-white-spaces-keeping-punctuation
    w = re.sub(r"([?.!,¿])", r" \1 ", w)
    w = re.sub(r'[" "]+', " ", w)

    # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
    # w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)
    # w = re.sub(r'\[.*?\]', '<ans>', w).rstrip().strip()
    w = w.rstrip().strip().lower()

    # adding a start and an end token to the sentence
    # so that the model know when to start and stop predicting.
    # w = '<start> ' + w + ' <end>'
    return w


def preprocess_sparql(s):
    for pre_name, pre_url in re.findall(r"PREFIX\s([^:]*):\s<([^>]+)>", s):
        s = re.sub(f"\\b{pre_name}:([^\\s]+)", f"<{pre_url}\\1>", s)
    # Remove prefixes
    s = re.sub(r"PREFIX\s[^\s]*\s[^\s]*", "", s)

    # replace sing quote to double quote
    s = re.sub(r"(\B')", '"', s)
    s = re.sub(r"'([^_A-Za-z])", r'"\1', s)

    # remove timezone 0
    s = re.sub(r"(\d{4}-\d{2}-\d{2})T00:00:00Z", r"\1", s)

    s = encode(s.rstrip().strip())

    normalize_s = []
    for token in s.split():
        beginning_subtoken = re.search(r"^\w+", token)
        if beginning_subtoken is not None:
            beginning_subtoken = beginning_subtoken.group()
            if beginning_subtoken.upper() in SPARQL_KEYWORDS:
                token = re.sub(r"^\w+", beginning_subtoken.lower(), token)
        normalize_s.append(token)

    s = " ".join(normalize_s)

    s = " ".join(s.split())

    return s

def preprocess_triples(triples):
    return [preprocess_sparql(triple) for triple in triples]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", dest="data_dir", required=True)
    parser.add_argument("--subset", dest="subset", required=True)
    parser.add_argument("--output", dest="output_dir", required=True)
    args = parser.parse_args()

    data_dir = args.data_dir
    subset = args.subset
    output_dir = args.output_dir

    data_dir = data_dir.rstrip("/")
    output_dir = output_dir.rstrip("/")

    with open(f"{output_dir}/{subset}.en", "w") as out:
        with open(f"{data_dir}/{subset}.en") as f:
            for line in f:
                if "\n" == line[-1]:
                    line = line[:-1]
                out.write(preprocess_sentence(line))
                out.write("\n")

    with open(f"{output_dir}/{subset}.sparql", "w") as out:
        with open(f"{data_dir}/{subset}.sparql") as f:
            for line in f:
                if "\n" == line[-1]:
                    line = line[:-1]
                out.write(preprocess_sparql(line))
                out.write("\n")

    with open(f"{output_dir}/{subset}.triple", "w") as out:
        with open(f"{data_dir}/{subset}.triple") as f:
            for line in f:
                if "\n" == line[-1]:
                    line = line[:-1]
                triples = line.split("\t")
                out.write("\t".join(preprocess_triples(triples)))
                out.write("\n")
