"""A module to summarize the triples for predicates from QALD8, QALD9 and LCQALD data set."""
from builtins import FileNotFoundError
import pickle
from typing import Dict
from typing import List
from typing import Tuple

from rdflib.graph import Graph
from rdflib.plugins.sparql import prepareQuery
from rdflib.term import URIRef
import requests
from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.Wrapper import RDFXML


def ask_for_entities(question: str, *, confidence: float = 0.8) -> List[URIRef]:
    """Named entities are returned for a given question.

    :param question: The question to be annotated.
    :param confidence: The confidence of the annotation.
    :return: list of rdflib.term.URIRef which are objects for URIs.
    """
    # Ask dbpedia spotlight for an annotation of question
    webserver_address = "https://api.dbpedia-spotlight.org/en/annotate"
    response = requests.post(
        webserver_address,
        data={"text": question, "confidence": confidence},
        headers={"Accept": "application/json"},
    ).json()
    print(response)
    # print(response["annotation"])
    # print(URIRef(response["annotation"]["surfaceForm"]["resource"][0]["@uri"]))
    named_entities: List[URIRef] = []
    # If no named entity found
    if "Resources" not in response:
        return named_entities
    # Else gather all named entities
    for resource in response["Resources"]:
        named_entities.append(URIRef(resource["@URI"]))

    return named_entities


def generate_sparql_string(
    entity: URIRef, list_of_predicates: List[Tuple[Tuple, int]]
) -> str:
    """
    Given entity and list of predicates. Sparql string for all predicates are returned.

    This function concatenate all entity-predicate-object triples in one big construct sparql query for dbpedia.
    DBpedia supposed to answer with a subgraph on this sparql string.

    :param entity: URIRef for which the query will be generated.
    :param list_of_predicates: list of predicates one or two hops from data set in sorted order from highest ranked predicate to lowest.
    :return: Construct sparql string.
    """
    string1 = ""
    string2 = ""
    subj1 = "<" + str(entity) + ">"
    first_predicate = True
    num = 1
    for pred in list_of_predicates:
        object1 = "?o" + str(num) + "."
        if len(pred[0]) != 2:
            pred1 = "<" + str(pred[0]) + ">"
            string1 = string1 + subj1 + pred1 + object1
            if first_predicate:
                string2 = string2 + """WHERE{{""" + subj1 + pred1 + object1 + """}"""
                first_predicate = False
            else:
                string2 = string2 + """UNION{""" + subj1 + pred1 + object1 + """}"""
            num = num + 1
        elif len(pred[0]) == 2:
            pred1 = "<" + str(pred[0][0]) + ">"
            pred2 = "<" + str(pred[0][1]) + ">"
            object1 = "?o" + str(num) + "."
            object11 = "?o" + str(num)
            object2 = "?o" + str(num) + "1."
            string1 = string1 + subj1 + pred1 + object1 + object11 + pred2 + object2
            if first_predicate:
                string2 = (
                    string2
                    + """WHERE{{"""
                    + subj1
                    + pred1
                    + object1
                    + object11
                    + pred2
                    + object2
                    + """}"""
                )
                first_predicate = False
            else:
                string2 = (
                    string2
                    + """UNION{"""
                    + subj1
                    + pred1
                    + object1
                    + object11
                    + pred2
                    + object2
                    + """}"""
                )
            num = num + 1
    string1 = """CONSTRUCT{""" + string1 + """}"""
    string2 = string2 + """}"""
    sparql_string = string1 + string2
    return sparql_string


def get_ranked_triples(
    entities: List[URIRef],
    *,
    limit: int = -1,
    number_of_triples: int = 100,
    number_triples_each_predicate: int = 10,
) -> List[URIRef]:
    """
    Given a list of entities from the question. List with necessary number of triples in ranked order is returned..

    :param entities: list of URIref of entities.
    :param limit: A natural number which limits the number of triples for each found entity.
    :param number_of_triples: necessary number of triples.
    :param number_triples_each_predicate: boundary of triples for each predicate and for each entity.
    :return: List of triples in URIref.
    """
    # Determine if we have a limit or not.
    if limit == -1:
        limit_str = ""
    else:
        limit_str = f"LIMIT {limit}"

    query_1hop = prepareQuery(
        f"""
        CONSTRUCT {{ ?s1 ?p1 ?o1 }}
        WHERE {{
            SERVICE <http://dbpedia.org/sparql> {{
                ?s1 ?p1 ?o1.
            }}
        }}
        {limit_str}
        """
    )
    query_2hop = prepareQuery(
        f"""
        CONSTRUCT {{ ?s1 ?p1 ?o1. ?o1 ?p2 ?o2 }}
        WHERE {{
            SERVICE <http://dbpedia.org/sparql> {{
                ?s1 ?p1 ?o1. ?o1 ?p2 ?o2
            }}
        }}
        {limit_str}
        """
    )
    with open("predicates_qald8.pickle", "rb") as file:
        rank_table = pickle.load(file)
        tripleslist = []
    for triples in rank_table:
        # query for one hope predicate and add triples from subgraph
        for entity in entities:
            subgraph = Graph()
            # This is only querying the service endpoint and not subgraph.
            if len(triples) == 1:
                subgraph_entity = subgraph.query(
                    query_1hop, initBindings={"s1": entity, "p1": triples[0]}
                )
            elif len(triples) == 2:
                # query for two hopes predicates, add triples from subgraph
                subgraph_entity = subgraph.query(
                    query_2hop,
                    initBindings={"s1": entity, "p1": triples[0], "p2": triples[1]},
                )
            for triple in subgraph_entity:
                if len(subgraph) == number_triples_each_predicate:
                    break
                subgraph.add(triple)
            for triple in subgraph:
                tripleslist.append(triple)
                if len(tripleslist) == number_of_triples:
                    return tripleslist
    return tripleslist


def query_dbpedia_for_all_entities(
    entities: List[URIRef], list_of_predicates: List[Tuple[Tuple, int]]
) -> Graph:
    """
    Given list of entities and list of predicates. Subgraph from DBPedia for all entities and predicates will be returned.

    This function generate sparql string, send request to DBPedia for all entities and given predicates and combined two subgraphs
    without triples duplicates.
    :param entities: list of entities from the question.
    :param list_of_predicates: predicates fom data set in decreasing order according rank.
    :return: triples_list for all entities without duplicates.
    """
    endpoint = "https://dbpedia.org/sparql"
    triples_list: List[Tuple] = []
    for entity in entities:
        sparql_string1 = generate_sparql_string(entity, list_of_predicates)
        sparql = SPARQLWrapper(
            endpoint,
            agent="Mozilla/5.0 (Windows NT x.y; Win64; x64; X11; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0",
        )
        sparql.setQuery(sparql_string1)
        sparql.method = "POST"
        sparql.setReturnFormat(RDFXML)
        graph_first_query = sparql.query().convert()
        triples_list = add_new_triples_without_duplicates_to_triples_list(
            triples_list, graph_first_query
        )
    return triples_list


def add_new_triples_without_duplicates_to_triples_list(
    triples_list: List[Tuple], graph: Graph
) -> List[Tuple]:
    """
    Given a subgraph from DBPedia with triples. Triples added to previous triples list without duplicates are returned.

    :param graph: subgraph of DBPedia.
    :param triples_list: previous triples list, where new triples will be added.
    :return: triples_list with new triples.
    """
    for triple in graph:
        if triple not in triples_list:
            triples_list.append(triple)
    return triples_list


def add_new_triples_without_duplicates_to_dict(
    triple: URIRef, predicate: URIRef, triples_list_sorted: Dict[Tuple, int]
) -> Dict[Tuple, int]:
    """
    Given triple and predicate and dictionary with triple:rank. Dictionary triple:rank together with new triple is returned.

    This function add triple to dictionary with triple:rank if this triple not in the dictionary.
    :param triple: triple URIRef.
    :param predicate: triple URIRef.
    :param triples_list_sorted: dictionary triple : rank.
    :return: triples_list_sorted with new triple.
    """
    if triple not in triples_list_sorted.keys():
        triples_list_sorted[triple] = predicate[1]

    return triples_list_sorted


def add_triples_for_entity_hop(
    entity: URIRef,
    predicate: URIRef,
    triples_list: List[Tuple],
    triples_list_sorted: Dict[Tuple, int],
    number_triples_each_predicate: int = 7,
) -> Dict[Tuple, int]:
    """
    Given entity, predicate and triples list. Two hop triples for entity and predicate added to final triple list in right order and necessary number and returned.

    This function adds two hops triples with rank for given entity and predicate in right order and necessary number in final triples list.
    :param entity: URIRef of entity from the question.
    :param predicate: URIRef of predicate.
    :param triples_list: triples_list to add.
    :param triples_list_sorted: dictionary with triple-rank in decreasing order.
    :param number_triples_each_predicate: how many triples for each predicate are needed.
    :return: triples_list_sorted with new triples.
    """
    break_flag = False
    i = 0
    for triple in triples_list:
        if predicate[0][0] == triple[1] and entity == triple[0]:
            for triple1 in triples_list:
                if predicate[0][1] == triple1[1] and triple[2] == triple1[0]:
                    triples_list_sorted = add_new_triples_without_duplicates_to_dict(
                        triple, predicate, triples_list_sorted
                    )
                    i = i + 1
                    triples_list_sorted = add_new_triples_without_duplicates_to_dict(
                        triple1, predicate, triples_list_sorted
                    )
                    i = i + 1
                    if i == number_triples_each_predicate:
                        break_flag = True
                        break
        if break_flag:
            break
    return triples_list_sorted


def add_triples_for_entity(
    entity: URIRef,
    predicate: URIRef,
    triples_list: List[Tuple],
    triples_list_sorted: Dict[Tuple, int],
    number_triples_each_predicate: int = 7,
) -> Dict[Tuple, int]:
    """
    Given entity, predicate and triples list. One hop triples for entity and predicate added to final triple list in right order and necessary number and returned.

    This function adds one hop triples with rank for given entity and predicate in right order and necessary
    number in final triples list.
    :param entity: URIRef of entity from the question.
    :param predicate: URIRef of predicate.
    :param triples_list: triples_list to add.
    :param triples_list_sorted: dictionary with triple-rank in decreasing order.
    :param number_triples_each_predicate: how many triples for each predicate are needed.
    :return: triples_list_sorted with new triples.
    """
    i = 0
    for triple in triples_list:
        if predicate[0] == triple[1] and entity == triple[0]:
            triples_list_sorted = add_new_triples_without_duplicates_to_dict(
                triple, predicate, triples_list_sorted
            )
            i = i + 1
            if i == number_triples_each_predicate:
                break
    return triples_list_sorted


def sort_triples_from_the_query(
    triples_list: List[Tuple],
    entities: List[URIRef],
    rank_table: List[Tuple],
    triples_list_sorted: Dict[Tuple, int],
) -> Dict[Tuple, int]:
    """
    Given a triples list from DBPedia and entities from the question, rank table with ranks in decreasing order. Triples for each predicate and each entity in sorted order will be returned.

    :param triples_list: triples for each entity and each predicate.
    :param entities: list of entities from the question.
    :param rank_table: list with tuples predicate:rank.
    :param triples_list_sorted: list with previous triples and ranks.
    :return: triples_list_sortet with new triples and their rank.
    """
    for predicate in rank_table:
        for entity in entities:
            if len(predicate[0]) == 2:
                triples_list_sorted = add_triples_for_entity_hop(
                    entity, predicate, triples_list, triples_list_sorted
                )
            else:
                triples_list_sorted = add_triples_for_entity(
                    entity, predicate, triples_list, triples_list_sorted
                )
    return triples_list_sorted


def triples_for_predicates_all_datasets(
    question: str,
    predicate_table: str,
    number_of_triples: int = 100,
) -> List[Tuple[Tuple, int]]:
    """
    Given question string, predicate_table and number of triples, that is needed. Necessary number of triples in ranked order are returned.

    This function sends sparql to DBPedia in order to get triples for each entity and each predicate
    in ranked order. The sparql requests will be sent until necessary number of triples are in the final list.

    :param question: question string in natural language.
    :param predicate_table: name of the file with predicates from data sets qald8, qald9, lcquad.
    :param number_of_triples: how many triples are needed.

    :return: final_triples_list with triples and rank.
    """
    entities = ask_for_entities(question)
    triples_list_sorted: Dict[Tuple, int] = {}
    final_triples_list: List[Tuple[Tuple, int]] = []
    try:
        with open(predicate_table, "rb") as file:
            predicates_table = pickle.load(file)
    except FileNotFoundError:
        pass
    num_of_query = 0
    first_pred = 0
    last_pred = 69
    while len(final_triples_list) < number_of_triples and num_of_query < 11:
        triples_list = query_dbpedia_for_all_entities(
            entities, predicates_table[first_pred:last_pred]
        )
        triples_list_sorted = sort_triples_from_the_query(
            triples_list,
            entities,
            predicates_table[first_pred:last_pred],
            triples_list_sorted,
        )
        final_triples_list = list(triples_list_sorted.items())
        num_of_query = num_of_query + 1
        first_pred = first_pred + 69
        last_pred = last_pred + 69
    final_triples_list = final_triples_list[0:number_of_triples]
    return final_triples_list


def main() -> None:
    """Call triples_for_predicates_all_datasets() to get triples with a rank for predicates from all data sets."""
    # triples = triples_for_predicates_all_datasets("Who is Justin Bieber?", "qald9_qald8_lcquad.pickle")
    # print(len(triples))
    # for triple in triples:
    #    print(triple)
    #    print("\n")
    # entities = ask_for_entities("Where is Washington")
    # print(entities)


# Call from shell as main.
if __name__ == "__main__":
    # start_time = time.time()
    main()
    # print(time.time() - start_time)
