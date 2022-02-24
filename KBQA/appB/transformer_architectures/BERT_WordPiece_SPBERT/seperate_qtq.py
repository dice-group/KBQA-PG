import argparse
import json


def filter_triples(triples: list) -> list:
    """
    Filter out triples containing \\n character.

    :param triples: list of triples
    :return: list of filtered triples
    """
    return [triple for triple in triples if not "\n" in triple]


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

    en_file = open(f"{output_dir}/{subset}.en", "w")
    sparql_file = open(f"{output_dir}/{subset}.sparql", "w")
    triple_file = open(f"{output_dir}/{subset}.triple", "w")
    data = json.load(open(f"{data_dir}/{subset}.json", "r"))
    for element in data["questions"]:
        en_file.write(element["question"] + "\n")
        sparql_file.write(element["query"] + "\n")
        triple_file.write("\t".join(filter_triples(element["triples"])) + "\n")

    en_file.close()
    sparql_file.close()
    triple_file.close()
