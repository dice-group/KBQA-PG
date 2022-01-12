"""A module to get ranking of triples from summarized subgraph."""
from contextlib import suppress
import json
import pickle
from typing import Dict
from typing import List
from typing import Tuple

from NES_NER_Hop.nes_ner_hop import nes_ner_hop_regular_and_inverse_subgraph
from rdflib.graph import Graph
from rdflib.plugins.sparql import algebra
from rdflib.plugins.sparql import parser
from rdflib.plugins.sparql.sparql import Query
from rdflib.term import URIRef


PICKLE_OBJECT_PATH = "ranking/pickle_objects/"


def load_sparql_from_json(jsonfile: str) -> List[str]:
    """
    Given a json file (for qald dataset) with train data, sparql strings of all the questions are returned.

    :param jsonfile: Path to json file.
    :return: List of all sparql striong from the given json file.
    """
    with open(jsonfile, encoding="utf8") as file:
        data_js = json.load(file)
    sparql_strings = []
    # parse all sparql strings from the json (works only for qald dataset)
    for question in data_js["questions"]:
        sparql_strings.append(question["query"]["sparql"])
    return sparql_strings


def load_sparql_from_json_lcqald(jsonfile: str) -> List[str]:
    """
    Given a json file (for LCQALD dataset) with train data, sparql strings of all the questions are returned.

    :param jsonfile: Path to json file as string.
    :return: List of all sparql strings from the given json file.
    """
    with open(jsonfile, encoding="utf8") as file:
        data_js = json.load(file)
    sparql_strings = []
    # parse all sparql strings (works only for LCQALD dataset)
    for question in data_js:
        sparql_strings.append(question["sparql_query"])
    return sparql_strings


def extract_triples_rec(query: Query) -> List[URIRef]:
    """
    Given a spaql.Query object(query), set of triples from sparql object are returned.

    This procedure extracts all possible triples from the sparql object.
    :param query: rdflib.plugins.sparql.sparql.Query object.
    :return: List of all triples from sparql object.
    """
    if not hasattr(query, "keys"):
        return []
    triples = []
    keys = query.keys()
    for key in keys:
        if key == "triples":
            value = query[key]
            if len(value) == 1:
                typestr = str(type(value[0][0]))
                subj = (typestr, value[0][0])
                typestr = str(type(value[0][1]))
                pred = (typestr, value[0][1])
                typestr = str(type(value[0][2]))
                obj = (typestr, value[0][2])
                triples.append((subj, pred, obj))
        else:
            newtriples = extract_triples_rec(query[key])
            for triple in newtriples:
                triples.append(triple)
    return triples


def extract_triples(sparql: str) -> List[URIRef]:
    """
    Given a spaql string, set of triples from sparql string are returned.

    This procedure parses sparql string to sparql object and extracts all possible triples from the sparql object.
    :param sparql: sparql string.
    :return: List of all triples from sparql string.
    """
    # get sparql tree from sparql string
    query_tree = parser.parseQuery(sparql)
    q_algebra = algebra.translateQuery(query_tree)
    triples = extract_triples_rec(q_algebra.algebra)
    return triples


def inverse_relations(tripleslist: list) -> List[URIRef]:
    """
    Given a list of triples, set of triples for inverse relations are returned.

    :param tripleslist: list of all triples from all sparql strings from dataset.
    :return: List of all triples for inverse relation.
    """
    inverse_triples_list = []
    # choose only triples where variable is on the left
    for triple_item in tripleslist:
        if "rdflib.term.Variable" in triple_item[0][0]:
            inverse_triples_list.append(triple_item)
    return inverse_triples_list


def relations(tripleslist: list) -> List[URIRef]:
    """
    Given a list of triples, set of triples for regular relations are returned.

    :param tripleslist: list of all triples from all sparql strings from dataset.
    :return: List of all triples for regular relation.
    """
    regular_triples_list = []
    # choose only triples where variable is on the right
    for triple_item in tripleslist:
        if "rdflib.term.Variable" in triple_item[2][0]:
            regular_triples_list.append(triple_item)
    return regular_triples_list


def predicate_count_relations(regular_triples_list: list) -> Dict[str, int]:
    """
    Given a list of triples for regular relation, dictionary of predicate - rank (occurrence of predicate) are returned.

    :param regular_triples_list: list of all triples for regular relation .
    :return: dictionary predicate-rank for regular relation.
    """
    relations_list = relations(regular_triples_list)
    regular_table = {}
    for triple_item in relations_list:
        key = str(triple_item[1][1])
        if key not in regular_table:
            regular_table[key] = 0
        regular_table[key] = regular_table[key] + 1
    return regular_table


def predicate_count_inverse_relations(inverse_triples_list: list) -> Dict[str, int]:
    """
    Given a list of triples for inverse relation, dictionary of predicate - rank (occurrence of predicate) are returned.

    :param inverse_triples_list: list of all triples for inverse relation .
    :return: dictionary predicate-rank for inverse relation.
    """
    inverse_relations_list = inverse_relations(inverse_triples_list)
    inverse_table = {}
    for triple_item in inverse_relations_list:
        key = str(triple_item[1][1])
        if key not in inverse_table:
            inverse_table[key] = 0
        inverse_table[key] = inverse_table[key] + 1
    return inverse_table


def get_ranking_tables(
    datasetfile: str, datasettype: str = "qald"
) -> Tuple[dict, dict]:
    """
    Given dataset file, two tables are returned.

    First table with predicate and rank for regular relation.
    The second table contains predicate and rank for inverse relation.

    :param datasetfile: path to json with dataset as string.
    :param datasettype: type of dataset (qald or lc-quad)
    :return: 2 dictionaries predicate, rank for inverse and regular relation.
    :raise ValueError: if datasettype is not qald or lc-quad.
    """
    if datasettype == "lc-quad":
        sparqllist = load_sparql_from_json_lcqald(datasetfile)
    elif datasettype == "qald":
        sparqllist = load_sparql_from_json(datasetfile)
    else:
        raise ValueError("Datasettype not supported.")

    tripleslist = []
    for sparql_item in sparqllist:
        with suppress(Exception):
            sparql_str = str(sparql_item)
            triples = extract_triples(sparql_str)
            for triple in triples:
                tripleslist.append(triple)
    image_list = relations(tripleslist)
    pre_image_list = inverse_relations(tripleslist)
    regular_table = predicate_count_relations(image_list)
    inverse_table = predicate_count_inverse_relations(pre_image_list)
    return regular_table, inverse_table


def rank_list(rank_table: dict, subgraph: Graph) -> dict:
    """
    Given table with rank for each predicate, and summarized subgraph. Dictionary with rank for each triples from subgraph are returned.

    :param rank_table: dictionary predicate-rank.
    :param subgraph: summarized subgraph.
    :return: dictionary with rank for each triples from subgraph.
    """
    subgraph_triples_ranked = {}
    for subgraph_item in subgraph:
        predicate = str(subgraph_item[1])
        if predicate in rank_table:
            subgraph_triples_ranked[subgraph_item] = rank_table[predicate]
        else:
            subgraph_triples_ranked[subgraph_item] = 0
    return subgraph_triples_ranked


def filter_table_until_last_rank(
    subgraph_triples_ranked: dict, limit: int
) -> Tuple[Dict, int]:
    """
    Given table with all triples of subgraph and rank for all of them. First "limit" + all triples with the last rank are returned.

    This procedure returns "limit" triples. If there are triples with the same rank in the table, they will be returned additionally.
    :param subgraph_triples_ranked: dictionary triples from subgraph-rank.
    :param limit: how many triples from subgraph are needed.
    :return: First "limit" triples from subgraph with highest rank + all triples with last rank, last_rank.
    """
    ranked_triples: dict = {}
    last_rank = 0
    for triple_item, rank in sorted(
        subgraph_triples_ranked.items(), key=lambda x: x[1], reverse=True
    ):

        if len(ranked_triples) < limit:
            ranked_triples[triple_item] = rank
            last_rank = rank
        else:
            if subgraph_triples_ranked[triple_item] == last_rank:
                ranked_triples[triple_item] = rank
            else:
                break
    return ranked_triples, last_rank


def filter_table(subgraph_triples_ranked: dict, limit: int) -> dict:
    """
    Given table with all triples of subgraph and rank for all of them. Given limit (how many triples from subgraphare needed). First "limit" triples with highest rank are returned.

    :param subgraph_triples_ranked: dictionary triples from subgraph-rank.
    :param limit: how many triples from subgraph are needed.
    :return: First "limit" triples from subgraph with highest rank.
    """
    ranked_triples: dict = {}
    for triple_item, rank in sorted(
        subgraph_triples_ranked.items(), key=lambda x: x[1], reverse=True
    ):

        if len(ranked_triples) < limit:
            ranked_triples[triple_item] = rank
    return ranked_triples


def ranked_triples_for_regular_subgraph(
    regular_subgraph: Graph, limit: int
) -> Dict[Tuple, int]:
    """
    Given Graph with triples for regular relation and number of necessary triples. Dictionary triple, rank are returned.

    This procedure returns "limit" triples. First triples are ranked according QALD dataset,
    in case number of triples with the smallest set makes result set larger than limit this triples will be ranked
    with LC_QALD dataset. Dictionary with "limit" triples are returned.

    :param regular_subgraph: Graph with triples for regular relation.
    :param limit: how many triples from subgraph are needed.
    :return: First "limit" triples from subgraph with highest rank.
    """
    with open(PICKLE_OBJECT_PATH + "regular_table.pickle", "rb") as file:
        regular_table = pickle.load(file)
    subgraph_triples_ranked = rank_list(regular_table, regular_subgraph)
    subgraph_triples_ranked, last_rank = filter_table_until_last_rank(
        subgraph_triples_ranked, limit
    )
    if len(subgraph_triples_ranked) == limit:
        return subgraph_triples_ranked
    else:
        triples_with_last_rank = Graph()
        regular_subgraph_triples_ranked = {}
        for triple_item, rank in subgraph_triples_ranked.items():
            if rank == last_rank:
                triples_with_last_rank.add(triple_item)
            else:
                regular_subgraph_triples_ranked[triple_item] = rank
        with open(PICKLE_OBJECT_PATH + "regular_table_lcqald.pickle", "rb") as file:
            regular_table = pickle.load(file)
        subgraph_triples_ranked = rank_list(regular_table, triples_with_last_rank)
        limit = limit - len(regular_subgraph_triples_ranked)
        subgraph_triples_ranked = filter_table(subgraph_triples_ranked, limit)
        regular_subgraph_triples_ranked = {
            **regular_subgraph_triples_ranked,
            **subgraph_triples_ranked,
        }
        return regular_subgraph_triples_ranked


def ranked_triples_for_inverse_subgraph(
    inverse_subgraph: Graph, limit: int
) -> Dict[Tuple, int]:
    """
    Given Graph with triples for inverse relation and number of necessary triples. Dictionary triple, rank are returned.

    This procedure returns "limit" triples. First triples are ranked according QALD dataset,
    in case number of triples with the smallest set makes result set larger than limit this triples will be ranked
    with LC_QALD dataset. Dictionary with "limit" triples are returned.

    :param inverse_subgraph: Graph with triples for inverse relation.
    :param limit: how many triples from subgraph are needed.
    :return: First "limit" triples from subgraph with highest rank.
    """
    with open(PICKLE_OBJECT_PATH + "inverse_table.pickle", "rb") as file:
        inverse_table = pickle.load(file)
    subgraph_triples_ranked = rank_list(inverse_table, inverse_subgraph)
    subgraph_triples_ranked, last_rank = filter_table_until_last_rank(
        subgraph_triples_ranked, limit
    )
    if len(subgraph_triples_ranked) == limit:
        return subgraph_triples_ranked
    else:
        triples_with_last_rank = Graph()
        inverse_subgraph_triples_ranked = {}
        for triple_item, rank in subgraph_triples_ranked.items():
            if rank == last_rank:
                triples_with_last_rank.add(triple_item)
            else:
                inverse_subgraph_triples_ranked[triple_item] = rank
        with open(PICKLE_OBJECT_PATH + "inverse_table_lcqald.pickle", "rb") as file:
            inverse_table = pickle.load(file)
        subgraph_triples_ranked = rank_list(inverse_table, triples_with_last_rank)
        limit = limit - len(inverse_subgraph_triples_ranked)
        subgraph_triples_ranked = filter_table(subgraph_triples_ranked, limit)
        inverse_subgraph_triples_ranked = {
            **inverse_subgraph_triples_ranked,
            **subgraph_triples_ranked,
        }
        return inverse_subgraph_triples_ranked


def main() -> None:
    """Call ranked_triples_for_regular_subgraph to get ranking of regular triples."""
    (
        regular_subgraph,
        inverse_subgraph,
    ) = nes_ner_hop_regular_and_inverse_subgraph(question="Who is Angela Merkel?")
    ranked_regular_triples = ranked_triples_for_regular_subgraph(regular_subgraph, 10)
    ranked_inverse_triples = ranked_triples_for_inverse_subgraph(inverse_subgraph, 20)
    for triple_item in ranked_inverse_triples.items():
        print(triple_item)
    print("\n")

    for triple_item in ranked_regular_triples.items():
        print(triple_item)
    print("\n")


# Call from shell as main.
if __name__ == "__main__":
    main()
