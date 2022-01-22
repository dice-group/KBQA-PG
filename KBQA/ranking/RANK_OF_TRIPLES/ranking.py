"""A module to get ranking of triples from summarized subgraph."""
from contextlib import suppress
import json
import pickle
from typing import Dict
from typing import List
from typing import Tuple

from rdflib.graph import Graph
from rdflib.plugins.sparql import algebra
from rdflib.plugins.sparql import parser
from rdflib.plugins.sparql.sparql import Query
from rdflib.term import URIRef


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
    Given a spaql.Query object(query), set of triples from sparql with only one triple object are returned.

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


def extract_hop_triples_rec(query: Query) -> List[URIRef]:
    """
    Given a spaql.Query object(query), set of triples from sparql with one or two hop are returned.

    This procedure extracts all possible triples from the sparql object with one or two hopes.
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
                subj1 = value[0][0]
                pred1 = value[0][1]
                obj1 = value[0][2]
                triples.append([(subj1, pred1, obj1)])
            else:
                if len(value) == 2:
                    if value[0][2] == value[1][0]:
                        subj1 = value[0][0]
                        pred1 = value[0][1]
                        obj1 = value[0][2]
                        subj2 = value[1][0]
                        pred2 = value[1][1]
                        obj2 = value[1][2]
                        triples.append([(subj1, pred1, obj1), (subj2, pred2, obj2)])
        else:
            newtriples = extract_hop_triples_rec(query[key])
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


def extract_hop_triples(sparql: str) -> List[URIRef]:
    """
    Given a spaql string, set of triples from sparql string are returned.

    This procedure parses sparql string to sparql object and extracts all possible triples from the sparql object.
    :param sparql: sparql string.
    :return: List of all triples from sparql string.
    """
    # get sparql tree from sparql string
    query_tree = parser.parseQuery(sparql)
    q_algebra = algebra.translateQuery(query_tree)
    triples_hop = extract_hop_triples_rec(q_algebra.algebra)
    return triples_hop


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
        predicate = str(triple_item[1][1])
        if predicate not in regular_table:
            regular_table[predicate] = 0
        regular_table[predicate] = regular_table[predicate] + 1
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
        predicate = str(triple_item[1][1])
        if predicate not in inverse_table:
            inverse_table[predicate] = 0
        inverse_table[predicate] = inverse_table[predicate] + 1
    return inverse_table


def predicate_count_with_multihop(
    tripleslist: List[List[URIRef]],
) -> List[List[URIRef]]:
    """
    Given lists with one or two hop triples. Lists with predicates for one or two hopes in sort order are returned.

    This procedure counts how many times one or two hopes predicates occur in the dataset QALD and
    returns lists with predicates with rank in decreasing order.
    :param tripleslist: lists with triples for one and two hopes.
    :return: lists with predicate for one or two hopes in decreasing order (ordered by rank).
    """
    rank_table = {}
    predicate_rank = []
    for triples_item in tripleslist:
        if len(triples_item) == 1:
            predicate = triples_item[0][1]
            if predicate not in rank_table:
                rank_table[predicate] = 0
            rank_table[predicate] = rank_table[predicate] + 1
        elif len(triples_item) == 2:
            predicate1_predicate2 = []
            predicate1 = triples_item[0][1]
            predicate2 = triples_item[1][1]
            predicate1_predicate2.append(predicate1)
            predicate1_predicate2.append(predicate2)
            predicates_tuple = tuple(predicate1_predicate2)
            if predicates_tuple not in rank_table:
                rank_table[predicates_tuple] = 0
            rank_table[predicates_tuple] = rank_table[predicates_tuple] + 1
    rank_table_list = sorted(rank_table.items(), key=lambda x: x[1], reverse=True)
    for item in rank_table_list:
        if isinstance(item[0], tuple):
            predicate_rank.append(list(item[0]))
        else:
            predicate_rank.append([item[0]])
    return predicate_rank


def get_ranking_tables(datasetfile: str) -> Tuple[dict, dict]:
    """
    Given dataset file, two tables are returned.

    First table with predicate and rank for regular relation.
    The second table contains predicate and rank for inverse relation.

    :param datasetfile: path to json with dataset as string.
    :return: 2 dictionaries predicate, rank for inverse and regular relation.
    """
    # sparqllist = load_sparql_from_json_lcqald(datasetfile)
    sparqllist = load_sparql_from_json(datasetfile)
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
    with open("regular_table.pickle", "rb") as file:
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
        with open("regular_table_lcqald.pickle", "rb") as file:
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
    with open("inverse_table.pickle", "rb") as file:
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
        with open("inverse_table_lcqald.pickle", "rb") as file:
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
    # (
    #    regular_subgraph,
    #    inverse_subgraph,
    # ) = nes_ner_hop_regular_and_inverse_subgraph(question="Who is Angela Merkel?")
    # ranked_regular_triples = ranked_triples_for_regular_subgraph(regular_subgraph, 100)
    # ranked_inverse_triples = ranked_triples_for_inverse_subgraph(inverse_subgraph, 1)
    # for triple_item in ranked_regular_triples.items():
    #    print(triple_item)
    #    print("\n")
    # print("\n")
    # print("\n")
    # for triple_item in ranked_inverse_triples.items():
    #    print(triple_item)
    #    print("\n")


# Call from shell as main.
if __name__ == "__main__":
    main()
