"""A module to summarize the triples for predicates from QALD8, QALD9 and LCQALD data set."""
from abc import ABC
from abc import abstractmethod
import pickle
from typing import Dict
from typing import List
from typing import Tuple

from rdflib.graph import Graph
from rdflib.term import Literal
from rdflib.term import URIRef
import requests
from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.Wrapper import RDFXML


class Triples_for_pred(ABC):
    """Abstract class for the summarizing triples for each entity."""

    def ask_for_entities(
        self, question: str, *, confidence: float
    ) -> Tuple[List[URIRef], float]:
        """Named entities and confidence are returned for a given question.

        :param question: The question to be annotated.
        :param confidence: The confidence of the annotation.
        :return: dictionary of rdflib.term.URIRef, which are objects for URIs and confidence.
        """
        confid = round(confidence, 1)
        # Ask dbpedia spotlight for an annotation of question
        webserver_address = "https://api.dbpedia-spotlight.org/en/annotate"
        response = requests.post(
            webserver_address,
            data={"text": question, "confidence": confidence},
            headers={"Accept": "application/json"},
        ).json()
        named_entities: List[URIRef] = []
        # If no named entity found
        if "Resources" not in response and confidence >= 0.1:
            named_entities, confid = self.ask_for_entities(
                question, confidence=confidence - 0.1
            )
        elif confidence < 0.1:
            return named_entities, confid
        elif "Resources" in response and confidence >= 0.1:
            # Else gather all named entities
            for resource in response["Resources"]:
                named_entities.append(URIRef(resource["@URI"]))
        return named_entities, confid

    def generate_sparql_string(
        self, entity: URIRef, list_of_predicates: List[Tuple[Tuple, int]]
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
                    string2 = (
                        string2 + """WHERE{{""" + subj1 + pred1 + object1 + """}"""
                    )
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

    def query_dbpedia_for_all_entities(
        self, entities: List[URIRef], list_of_predicates: List[Tuple[Tuple, int]]
    ) -> Graph:
        """
        Given list of entities and list of predicates. Subgraph from DBPedia for all entities and predicates will be returned.

        This function generate sparql string, send request to DBPedia for all entities and given predicates and combined two subgraphs
        without triples duplicates.
        :param entities: list of entities from the question.
        :param list_of_predicates: predicates from data set in decreasing order according rank.
        :return: triples_list for all entities without duplicates.
        """
        endpoint = "https://dbpedia.org/sparql"
        triples_list: List[Tuple] = []
        for entity in entities:
            sparql_string1 = self.generate_sparql_string(entity, list_of_predicates)
            sparql = SPARQLWrapper(
                endpoint,
                agent="Mozilla/5.0 (Windows NT x.y; Win64; x64; X11; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0",
            )
            sparql.setQuery(sparql_string1)
            sparql.method = "POST"
            sparql.setReturnFormat(RDFXML)
            graph_first_query = sparql.query().convert()
            triples_list = self.add_new_triples_without_duplicates_to_triples_list(
                triples_list, graph_first_query
            )
        return triples_list

    @abstractmethod
    def add_new_triples_without_duplicates_to_triples_list(
        self, triples_list: List[Tuple], graph: Graph
    ) -> List[Tuple]:
        """
        Given a subgraph from DBPedia with triples. Triples added to previous triples list without duplicates are returned.

        This function adds triples from the DBPedia graph to list of all triples without duplicates
        and without triples with "Literal" not in English language.
        :param graph: subgraph of DBPedia.
        :param triples_list: previous triples list, where new triples will be added.
        """

    def add_new_triples_without_duplicates_to_dict(
        self,
        triple: URIRef,
        predicate: URIRef,
        triples_dict_sorted: Dict[Tuple[URIRef, URIRef, URIRef], int],
    ) -> Dict[Tuple[URIRef, URIRef, URIRef], int]:
        """
        Given triple and predicate and dictionary with triple:rank. Dictionary triple:rank together with new triple is returned.

        This function add triple to dictionary with triple:rank if this triple not in the dictionary.
        :param triple: triple URIRef.
        :param predicate: triple URIRef.
        :param triples_dict_sorted: dictionary triple : rank.
        :return: triples_dict_sorted with new triple.
        """
        if triple not in triples_dict_sorted.keys():
            triples_dict_sorted[triple] = predicate[1]

        return triples_dict_sorted

    def add_triples_for_entity_hop(
        self,
        entity: URIRef,
        predicate: URIRef,
        triples_list: List[Tuple[URIRef, URIRef, URIRef]],
        triples_dict_sorted: Dict[Tuple[URIRef, URIRef, URIRef], int],
        number_triples_each_predicate: int = 7,
    ) -> Dict[Tuple[URIRef, URIRef, URIRef], int]:
        """
        Given entity, predicate and triples list. Two hop triples for entity and predicate added to final triple list in right order and necessary number and returned.

        This function adds two hops triples with rank for given entity and predicate in right order and necessary number in final triples list.
        :param entity: URIRef of entity from the question.
        :param predicate: URIRef of predicate.
        :param triples_list: triples_list to add.
        :param triples_dict_sorted: dictionary with triple-rank in decreasing order.
        :param number_triples_each_predicate: how many triples for each predicate are needed.
        :return: triples_dict_sorted with new triples.
        """
        break_flag = False
        i = 0
        for triple in triples_list:
            if predicate[0][0] == triple[1] and entity == triple[0]:
                for triple1 in triples_list:
                    if predicate[0][1] == triple1[1] and triple[2] == triple1[0]:
                        triples_dict_sorted = (
                            self.add_new_triples_without_duplicates_to_dict(
                                triple, predicate, triples_dict_sorted
                            )
                        )
                        i = i + 1
                        triples_dict_sorted = (
                            self.add_new_triples_without_duplicates_to_dict(
                                triple1, predicate, triples_dict_sorted
                            )
                        )
                        i = i + 1
                        if i == number_triples_each_predicate:
                            break_flag = True
                            break
            if break_flag:
                break
        return triples_dict_sorted

    def add_triples_for_entity(
        self,
        entity: URIRef,
        predicate: URIRef,
        triples_list: List[Tuple[URIRef, URIRef, URIRef]],
        triples_dict_sorted: Dict[Tuple[URIRef, URIRef, URIRef], int],
        number_triples_each_predicate: int = 7,
    ) -> Dict[Tuple[URIRef, URIRef, URIRef], int]:
        """
        Given entity, predicate and triples list. One hop triples for entity and predicate added to final triple list in right order and necessary number and returned.

        This function adds one hop triples with rank for given entity and predicate in right order and necessary
        number in final triples list.
        :param entity: URIRef of entity from the question.
        :param predicate: URIRef of predicate.
        :param triples_list: triples_list to add.
        :param triples_dict_sorted: dictionary with triple-rank in decreasing order.
        :param number_triples_each_predicate: how many triples for each predicate are needed.
        :return: triples_dict_sorted with new triples.
        """
        i = 0
        for triple in triples_list:
            if predicate[0] == triple[1] and entity == triple[0]:
                triples_dict_sorted = self.add_new_triples_without_duplicates_to_dict(
                    triple, predicate, triples_dict_sorted
                )
                i = i + 1
                if i == number_triples_each_predicate:
                    break
        return triples_dict_sorted

    def sort_triples_from_the_query(
        self,
        triples_list: List[Tuple[URIRef, URIRef, URIRef]],
        entities: List[URIRef],
        rank_table: List[Tuple[URIRef, int]],
        triples_dict_sorted: Dict[Tuple[URIRef, URIRef, URIRef], int],
    ) -> Dict[Tuple[URIRef, URIRef, URIRef], int]:
        """
        Given a triples list from DBPedia and entities from the question, rank table with ranks in decreasing order. Triples for each predicate and each entity in sorted order will be returned.

        :param triples_list: triples for each entity and each predicate.
        :param entities: dictionary of entities from the question.
        :param rank_table: list with tuples predicate:rank.
        :param triples_dict_sorted: list with previous triples and ranks.
        :return: triples_dict_sortet with new triples and their rank.
        """
        for predicate in rank_table:
            for entity in entities:
                if len(predicate[0]) == 2:
                    triples_dict_sorted = self.add_triples_for_entity_hop(
                        entity, predicate, triples_list, triples_dict_sorted
                    )
                else:
                    triples_dict_sorted = self.add_triples_for_entity(
                        entity, predicate, triples_list, triples_dict_sorted
                    )
        return triples_dict_sorted

    def add_confidence(
        self,
        triples_list_sorted: List[Tuple[Tuple[URIRef, URIRef, URIRef], int]],
        confid: float,
    ) -> List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]:
        """
        Given a list of tuples(triple, rank). List of tuples (triple,rank,confidence) is returned.

        :param triples_list_sorted: list of tuples (triple, rank).
        :param confid: confidence score.
        :return: final triples list of tuples (triple, rank, confidence).
        """
        final_triples_list: List[
            Tuple[Tuple[URIRef, URIRef, URIRef], float, float]
        ] = []
        for triple in triples_list_sorted:
            # trip_list = list(triple)
            # trip_list.append(confid)
            # final_triples_list.append(tuple(trip_list))
            final_triples_list.append((triple[0], float(triple[1]), confid))
        return final_triples_list

    def get_triples_final(
        self,
        question: str,
        predicate_table: str,
        number_of_trip: int,
        confidence: float,
    ) -> List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]:
        """
        Given question string, predicate_table and number of triples, that is needed. Necessary number of triples in ranked order are returned.

        This function sends sparql to DBPedia in order to get triples for each entity and each predicate
        in ranked order. The sparql requests will be sent until necessary number of triples are in the final list.

        :param question: question string in natural language.
        :param predicate_table: name of the file with predicates from data sets qald8, qald9, lcquad.
        :param number_of_trip: how many triples are needed.
        :param confidence: confidence score.

        :return: triples_list_sorted with triples and rank.
        """
        entities, confidence = self.ask_for_entities(question, confidence=confidence)
        triples_dict_sorted: Dict[Tuple[URIRef, URIRef, URIRef], int] = {}
        triples_list_sorted: List[Tuple[Tuple[URIRef, URIRef, URIRef], int]] = []

        with open(predicate_table, "rb") as file:
            predicates_table = pickle.load(file)

        num_of_query = 0
        first_pred = 0
        last_pred = 66
        while len(triples_list_sorted) < number_of_trip and num_of_query < 17:
            triples_list = self.query_dbpedia_for_all_entities(
                entities, predicates_table[first_pred:last_pred]
            )
            triples_dict_sorted = self.sort_triples_from_the_query(
                triples_list,
                entities,
                predicates_table[first_pred:last_pred],
                triples_dict_sorted,
            )
            triples_list_sorted = list(triples_dict_sorted.items())
            num_of_query = num_of_query + 1
            first_pred = first_pred + 66
            last_pred = last_pred + 66
        triples_list_sorted = triples_list_sorted[0:number_of_trip]
        final_triples_list = self.add_confidence(triples_list_sorted, confidence)
        return final_triples_list


class Triples_for_pred_with_filter(Triples_for_pred):
    """Class for the summarizing triples for each entity with filtering of triples."""

    def add_new_triples_without_duplicates_to_triples_list(
        self, triples_list: List[Tuple], graph: Graph
    ) -> List[Tuple]:
        """
        Given a subgraph from DBPedia with triples. Triples added to previous triples list without duplicates are returned.

        This function adds triples from the DBPedia graph to list of all triples without duplicates
        and without triples with "Literal" not in English language.
        :param graph: subgraph of DBPedia.
        :param triples_list: previous triples list, where new triples will be added.
        :return: triples_list with new triples.
        """
        for triple in graph:
            if triple not in triples_list:
                if not isinstance(triple[2], Literal):
                    triples_list.append(triple)
                elif isinstance(triple[2], Literal) and triple[2].language == "en":
                    triples_list.append(triple)

        return triples_list


class Triples_for_pred_no_filter(Triples_for_pred):
    """Class for the summarizing triples for each entity without filtering of triples."""

    def add_new_triples_without_duplicates_to_triples_list(
        self, triples_list: List[Tuple], graph: Graph
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


def triples_for_predicates_all_datasets(
    question: str,
    predicate_table: str,
    filtering: bool,
    number_of_triples: int = 100,
    confidence: float = 0.8,
) -> List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]:
    """
    Given question string, predicate_table. Necessary number of triples in ranked order are returned.

    :param question: question string in natural language.
    :param predicate_table: name of the file with predicates from data sets qald8, qald9, lcquad.
    :param filtering: True if we need only triples, where Literal in English.
    :param number_of_triples: how many triples are needed.
    :param confidence: start confidence score.
    :return: final_triples_list of tuples(triple, rank, confidence).
    """
    if filtering:
        triples_object = Triples_for_pred_with_filter()
        final_triples_list = triples_object.get_triples_final(
            question,
            predicate_table,
            number_of_trip=number_of_triples,
            confidence=confidence,
        )
    else:
        triples_object1 = Triples_for_pred_no_filter()
        final_triples_list = triples_object1.get_triples_final(
            question,
            predicate_table,
            number_of_trip=number_of_triples,
            confidence=confidence,
        )
    return final_triples_list


def main() -> None:
    """Call triples_for_predicates_all_datasets() to get triples with a rank for predicates from all data sets."""
    triples = triples_for_predicates_all_datasets(
        "How large is the area of UK?",
        "pickle_objects/qald8_qald9_lcquad.pickle",
        True,
        number_of_triples=100,
        confidence=0.8,
    )
    print(len(triples))
    # for triple in triples:
    #    print(triple)
    #    print("\n")


# Call from shell as main.
if __name__ == "__main__":
    # start_time = time.time()
    main()
    # print(time.time() - start_time)
