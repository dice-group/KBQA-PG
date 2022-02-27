"""Module for postprocessing a query predicted by BERT_wordpiece_SPBERT."""
import re
from typing import Dict

from app.arguments.args_postprocessing import POSTPROCESSING
from app.bert_wordpiece_spbert.generator_utils import decode


def postprocessing() -> Dict[str, str]:
    """Postprocessing of a predicted query written in a file.

    Returns
    -------
    queries : dict
        Dictionary containing the ids of the queries as keys and
        the postprocessed SPARQL-queries as values.
    """
    args = POSTPROCESSING

    predict_dir = args.predict_dir
    predict_file = args.predict_file

    predict_dir = predict_dir.rstrip("/")

    queries = {}

    with open(f"{predict_dir}/{predict_file}", "r", encoding="utf-8") as output_file:
        for line in output_file:
            line = re.sub(r"\s+", " ", line)
            query_pair = line.split(" ", 1)

            query_number = query_pair[0]
            query_decoded = decode(query_pair[1])
            # query_decoded = fix_URI(query_decoded)
            query_decoded = query_decoded.replace("<", "").replace(">", "")

            queries[query_number] = query_decoded

    return queries


if __name__ == "__main__":
    postprocessing()
