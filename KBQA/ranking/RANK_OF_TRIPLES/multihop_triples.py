"""A module to summarize the triples for predicates from QALD8, QALD9 and LCQALD data set."""
from abc import ABC
from abc import abstractmethod
from builtins import FileNotFoundError
from json.decoder import JSONDecodeError
import pickle
import time
from typing import Dict
from typing import List
from typing import Tuple

from KBQA.appB.summarizers.utils import entity_recognition_tagme
from KBQA.ranking.RANK_OF_TRIPLES.Relatedness_triples import calclualteRelatenessOfGraphs
from KBQA.ranking.RANK_OF_TRIPLES.Relatedness_triples import dictTripleRelateness
from KBQA.ranking.RANK_OF_TRIPLES.Relatedness_triples import graphs_for_the_question
from rdflib.graph import Graph
from rdflib.term import Literal
from rdflib.term import URIRef
import requests
from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.Wrapper import RDFXML


class Triples_for_pred(ABC):
    """Abstract class for the summarizing triples for each entity."""

    def ask_for_entities_dbpedia(
        self, question: str, *, confidence: float
    ) -> Tuple[List[URIRef], float]:
        """Named entities and confidence are returned from dbpedia for a given question.

        --------------
        :param question: The question to be annotated.
        :param confidence: The confidence of the annotation.
        :return: tuple list of rdflib.term.URIRef, which are objects for URIs and confidence.
        """
        confid = round(confidence, 1)
        named_entities: List[URIRef] = []
        # Ask dbpedia spotlight for an annotation of question
        webserver_address = "https://api.dbpedia-spotlight.org/en/annotate"
        try:
            response = requests.post(
                webserver_address,
                data={"text": question, "confidence": confidence},
                headers={"Accept": "application/json"},
            ).json()
        except JSONDecodeError:
            print("It was not possible to parse the answer.")
            return named_entities, confid
        # If no named entity found
        if "Resources" not in response and confidence >= 0.1:
            named_entities, confid = self.ask_for_entities_dbpedia(
                question, confidence=confidence - 0.1
            )
        elif confidence < 0.1:
            return named_entities, confid
        elif "Resources" in response and confidence >= 0.1:
            # Else gather all named entities
            for resource in response["Resources"]:
                named_entities.append(URIRef(resource["@URI"]))
        return named_entities, confid

    def ask_for_entities(
        self, question: str, *, confidence: float
    ) -> Tuple[List[URIRef], float]:
        """Named entities and confidence are returned from DBPedia + Tagme for a given question.

        --------------
        :param question: The question to be annotated.
        :param confidence: The confidence of the annotation.
        :return: Tuple List of rdflib.term.URIRef, which are objects for URIs and confidence.
        """
        entities, confidence = self.ask_for_entities_dbpedia(
            question, confidence=confidence
        )
        entities_tagme = entity_recognition_tagme(question, conf=confidence)
        for entity in entities_tagme:
            if entity[0] not in entities:
                entities.append(entity[0])
        print("Y ENTITIES:", entities)
        return entities, confidence

    def generate_sparql_string(
        self, entity: URIRef, list_of_predicates: List[Tuple[Tuple, int]]
    ) -> str:
        """
        Given entity and list of predicates. Sparql string for all predicates are returned.

        This function concatenate all entity-predicate-object triples in one big construct sparql query for dbpedia.
        DBpedia supposed to answer with a subgraph on this sparql string.
        --------------
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
            object1 = "?obj1" + str(num) + "."
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
                object1 = "?obj" + str(num) + "."
                object11 = "?obj" + str(num)
                object2 = "?obj" + str(num) + "1."
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

    def generate_sparql_string_inverse(
        self, entity: URIRef, list_of_predicates: List[Tuple[Tuple, int]]
    ) -> str:
        """
        Given entity and list of predicates. Sparql string for all predicates for inverse subgraph are returned.

        This function concatenate all entity-predicate-object triples in one big construct sparql query for dbpedia.
        DBpedia supposed to answer with a subgraph on this sparql string.
        --------------
        :param entity: URIRef for which the query will be generated.
        :param list_of_predicates: list of predicates one or two hops from data set in sorted order from highest ranked predicate to lowest.
        :return: Construct sparql string.
        """
        string1 = ""
        string2 = ""
        first_predicate = True
        num = 1
        object2 = "<" + str(entity) + ">."
        for pred in list_of_predicates:
            subj1 = "?s" + str(num)
            if len(pred[0]) != 2:
                pred1 = "<" + str(pred[0]) + ">"
                string1 = string1 + subj1 + pred1 + object2
                if first_predicate:
                    string2 = (
                        string2 + """WHERE{{""" + subj1 + pred1 + object2 + """}"""
                    )
                    first_predicate = False
                else:
                    string2 = string2 + """UNION{""" + subj1 + pred1 + object2 + """}"""
                num = num + 1
        string1 = """CONSTRUCT{""" + string1 + """}"""
        string2 = string2 + """} LIMIT 5000"""
        sparql_string = string1 + string2
        return sparql_string

    def query_dbpedia_for_all_entities(
        self, entities: List[URIRef], list_of_predicates: List[Tuple[Tuple, int]]
    ) -> Graph:
        """
        Given list of entities and list of predicates. Subgraph from DBPedia for all entities and predicates will be returned.

        This function generate sparql string, send request to DBPedia for all entities and given predicates and combined two subgraphs
        without triples duplicates.
        --------------
        :param entities: list of entities from the question.
        :param list_of_predicates: predicates from data set in decreasing order according rank.
        :return: triples_list for all entities without duplicates.
        """
        endpoint = "https://dbpedia.org/sparql"
        triples_list: List[Tuple] = []
        for entity in entities:
            sparql_string1 = self.generate_sparql_string(entity, list_of_predicates)
            sparql_string2 = self.generate_sparql_string_inverse(
                entity, list_of_predicates
            )
            sparql = SPARQLWrapper(
                endpoint,
                agent="Mozilla/5.0 (Windows NT x.y; Win64; x64; X11; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0",
            )
            sparql.setQuery(sparql_string1)
            sparql.method = "POST"
            sparql.setReturnFormat(RDFXML)
            graph_first_query = sparql.query().convert()
            triples_list1 = self.add_new_triples_without_duplicates_to_triples_list(
                triples_list, graph_first_query
            )
            sparql.setQuery(sparql_string2)
            sparql.method = "POST"
            sparql.setReturnFormat(RDFXML)
            graph_first_query = sparql.query().convert()
            triples_list2 = self.add_new_triples_without_duplicates_to_triples_list(
                triples_list, graph_first_query
            )

            triples_list = triples_list1 + triples_list2

        return triples_list

    @abstractmethod
    def add_new_triples_without_duplicates_to_triples_list(
        self, triples_list: List[Tuple], graph: Graph
    ) -> List[Tuple]:
        """
        Given a subgraph from DBPedia with triples. Triples added to previous triples list without duplicates are returned.

        This function adds triples from the DBPedia graph to list of all triples without duplicates
        and without triples with "Literal" not in English language.
        --------------
        :param graph: subgraph of DBPedia.
        :param triples_list: previous triples list, where new triples will be added.
        """

    def add_new_triples_without_duplicates_to_dict(
        self, triple: URIRef, predicate: URIRef, triples_dict_sorted: Dict[Tuple, int]
    ) -> Dict[Tuple, int]:
        """
        Given triple and predicate and dictionary with triple:rank. Dictionary triple:rank together with new triple is returned.

        This function add triple to dictionary with triple:rank if this triple not in the dictionary.
        --------------
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
        triples_list: List[Tuple],
        triples_dict_sorted: Dict[Tuple, int],
        number_triples_each_predicate: int = 3,
    ) -> Dict[Tuple, int]:
        """
        Given entity, predicate and triples list. Two hop triples for entity and predicate added to final triple list in right order and necessary number and returned.

        This function adds two hops triples with rank for given entity and predicate in right order and necessary number in final triples list.
        --------------
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
        triples_list: List[Tuple],
        triples_dict_sorted: Dict[Tuple, int],
        number_triples_each_predicate: int = 3,
    ) -> Dict[Tuple, int]:
        """
        Given entity, predicate and triples list. One hop triples for entity and predicate added to final triple list in right order and necessary number and returned.

        This function adds one hop triples with rank for given entity and predicate in right order and necessary
        number in final triples list.
        --------------
        :param entity: URIRef of entity from the question.
        :param predicate: URIRef of predicate.
        :param triples_list: triples_list to add.
        :param triples_dict_sorted: dictionary with triple-rank in decreasing order.
        :param number_triples_each_predicate: how many triples for each predicate are needed.
        :return: triples_dict_sorted with new triples.
        """
        i = 0
        for triple in triples_list:
            if predicate[0] == triple[1] and entity in (triple[0], triple[2]):
                triples_dict_sorted = self.add_new_triples_without_duplicates_to_dict(
                    triple, predicate, triples_dict_sorted
                )
                i = i + 1
                if i == number_triples_each_predicate:
                    break
        return triples_dict_sorted

    def sort_triples_from_the_query(
        self,
        triples_list: List[Tuple],
        entities: List[URIRef],
        rank_table: List[Tuple],
        triples_dict_sorted: Dict[Tuple, int],
    ) -> Dict[Tuple, int]:
        """
        Given a triples list from DBPedia and entities from the question, rank table with ranks in decreasing order. Triples for each predicate and each entity in sorted order will be returned.

        --------------
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
        self, triples_list_sorted: List[Tuple[Tuple, int]], confid: float
    ) -> List[Tuple]:
        """
        Given a list of tuples(triple, rank). List of tuples (triple,rank,confidence) is returned.

        --------------
        :param triples_list_sorted: list of tuples (triple, rank).
        :param confid: confidence score.
        :return: final triples list of tuples (triple, rank, confidence).
        """
        final_triples_list = []
        for triple in triples_list_sorted:
            trip_list = list(triple)
            trip_list.append(confid)
            final_triples_list.append(tuple(trip_list))
        return final_triples_list

    def get_triples_final(
        self,
        question: str,
        predicate_table: str,
        number_of_trip: int,
        confidence: float,
    ) -> List[Tuple]:
        """
        Given question string, predicate_table and number of triples, that is needed. Necessary number of triples in ranked order are returned.

        This function sends sparql to DBPedia in order to get triples for each entity and each predicate
        in ranked order. The sparql requests will be sent until necessary number of triples are in the final list.

        --------------
        :param question: question string in natural language.
        :param predicate_table: name of the file with predicates from data sets qald8, qald9, lcquad.
        :param number_of_trip: how many triples are needed.
        :param confidence: confidence score.

        :return: triples_list_sorted with triples and rank.
        """
        entities, confidence = self.ask_for_entities(question, confidence=confidence)
        triples_dict_sorted: Dict[Tuple, int] = {}
        triples_list_sorted: List[Tuple[Tuple, int]] = []
        try:
            with open(predicate_table, "rb") as file:
                predicates_table = pickle.load(file)
        except FileNotFoundError:
            pass
        num_of_query = 0
        first_pred = 0
        last_pred = 60
        while len(triples_list_sorted) < number_of_trip and num_of_query < 18:
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
            first_pred = first_pred + 60
            last_pred = last_pred + 60
        triples_list_sorted = triples_list_sorted[0:number_of_trip]
        if len(triples_list_sorted) < number_of_trip:
            triples_list_sorted = self.add_relatedness_triples(
                triples_list_sorted, entities, number_of_trip - len(triples_list_sorted)
            )
        final_triples_list = self.add_confidence(triples_list_sorted, confidence)
        return final_triples_list

    def add_relatedness_triples(
        self,
        triples_list_sorted: List[Tuple[Tuple, int]],
        entities: List[URIRef],
        number_of_triples: int,
    ) -> List[Tuple[Tuple, int]]:
        """
        Given a triples list with rank, entities and number_of_triples to add. Triples list with rank with added triples is returned.

        This function adds triples which are similar for different entities from the question.
        --------------
        :param triples_list_sorted: triples with rank.
        :param entities: list of entities.
        :param number_of_triples: number of triples to add
        :return: triples_list_sorted with added triples.
        """
        graphs = graphs_for_the_question(entities)
        tupleRelatedness = calclualteRelatenessOfGraphs(graphs)
        tripleRelatedness = dictTripleRelateness(tupleRelatedness)
        triples_added = 0
        for triple in tripleRelatedness:
            if triple not in dict(triples_list_sorted).keys():
                triples_list_sorted.append((triple, 1))
                triples_added = triples_added + 1
            if triples_added == number_of_triples:
                break
        return triples_list_sorted


class Triples_for_pred_with_filter(Triples_for_pred):
    """Class for the summarizing triples for each entity with filtering of triples."""

    def add_new_triples_without_duplicates_to_triples_list(
        self,
        triples_list: List[Tuple],
        graph: Graph,
    ) -> List[Tuple]:
        """
        Given a subgraph from DBPedia with triples. Triples added to previous triples list without duplicates are returned.

        This function adds triples from the DBPedia graph to list of all triples without duplicates
        and without triples with "Literal" not in English language.
        --------------
        :param graph: subgraph of DBPedia.
        :param triples_list: previous triples list, where new triples will be added.
        :return: triples_list with new triples.
        """
        for triple in graph:
            graph.triples(triple)
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

        --------------
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
    confidence: float = 0.3,
) -> List[Tuple]:
    """
    Given question string, predicate_table. Necessary number of triples in ranked order are returned.

    --------------
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
    # m = Triples_for_pred_no_filter()
    # entity = rdflib.term.URIRef('http://dbpedia.org/resource/Abraham_Lincoln')
    # entity2 = rdflib.term.URIRef('http://dbpedia.org/resource/Mary_Todd_Lincoln')
    # try:
    #    with open("qald9_qald8_lcquad.pickle", "rb") as file:
    #        list_of_predicates = pickle.load(file)
    # except FileNotFoundError:
    #    pass
    # graph = m.query_dbpedia_for_entity(entity2, list_of_predicates)
    # ent = m.ask_for_entities("Which politicians were married to a German?", confidence = 0.4)
    # print(ent)
    # triples = triples_for_predicates_all_datasets(
    #    "Vladimir Putin, Donald Trump",
    #    "qald9_qald8_lcquad.pickle",
    #    True,
    #    number_of_triples=100,
    #    confidence=0.3,
    # )
    # print(len(triples))
    # for triple in triples:
    #    print(triple)
    #    print("\n")


# Call from shell as main.
if __name__ == "__main__":
    start_time = time.time()
    main()
    print(time.time() - start_time)
