"""A module to summarize the triples based on relatedness."""
from contextlib import suppress
from typing import Dict
from typing import List
from typing import Tuple

from nltk.corpus import wordnet
from rdflib.graph import Graph
from rdflib.term import Literal
from rdflib.term import URIRef
from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.Wrapper import RDFXML


def graphs_for_the_question(entities: List[URIRef]) -> List[Graph]:
    """
    Given a list of entities. List of subgraphs for each entity is returned.

    This function asks DBPedia for direct and inverse subgraph for each entity and returns Subgraph for each entity.
    --------------
    :param entities: list of entities in URIRef format.
    :return: list of graphs.
    """
    endpoint = "https://dbpedia.org/sparql"
    graph_list = list()
    for entity in entities:
        sparql_string1 = f"""CONSTRUCT WHERE{{
            <{entity}> ?p ?o.
            }}
            """
        sparql_string2 = f"""CONSTRUCT WHERE{{
            ?s ?p <{entity}>.
            }}
            """
        sparql = SPARQLWrapper(
            endpoint,
            agent="Mozilla/5.0 (Windows NT x.y; Win64; x64; X11; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0",
        )
        sparql.setQuery(sparql_string1)
        sparql.method = "POST"
        sparql.setReturnFormat(RDFXML)
        graph1 = sparql.query().convert()
        sparql.setQuery(sparql_string2)
        sparql.method = "POST"
        sparql.setReturnFormat(RDFXML)
        graph2 = sparql.query().convert()
        graph_list.append(graph1 + graph2)
    return graph_list


def calclualteRelatenessOfGraphs(graphs: List[Graph]) -> Dict[Tuple, float]:
    """
    Given a list of graphs. Dictionary with tuple of two triples-relatedness score is returned .

    This function computes relatedness between all pair of triples from different
    graphs(different entities) and returnes it in decreasing order of relatedness.
    --------------
    :param graphs: list of subgraphs for entities.
    :return: dictionary tuple(triple, triple)- relatedness.
    """
    # list of dict, each dict is for a graph from the graph list, it maps label to triple
    graphsLabelsToTriples = []
    # list of lists, each list contains the Hypernyms for a label+ the label itself on the end of the list
    graphsLabelsHypernyms = []
    for graph in graphs:
        # dict for mapping label to triple
        labelsToTriples = getLabelsToTriples(graph)
        # add the previous dict to the list(we do that for each graph)
        graphsLabelsToTriples.append(labelsToTriples)
        # we get the labels from the dict
        labels = list(labelsToTriples.keys())
        # we find the Hypernyms for the labels list in each graph
        graphsLabelsHypernyms.append(getHypernymsPerList(labels))

    pairDict = {}
    graphNumber1 = 0
    while graphNumber1 < len(graphsLabelsHypernyms) - 1:
        graph1LabelsHypernyms = graphsLabelsHypernyms[graphNumber1]
        graphNumber2 = graphNumber1 + 1
        while graphNumber2 < len(graphsLabelsHypernyms):
            for hypernyms1 in graph1LabelsHypernyms:
                for hypernyms2 in graphsLabelsHypernyms[graphNumber2]:
                    relatedness = calculateRelatedness(hypernyms1, hypernyms2)
                    triple1 = graphsLabelsToTriples[graphNumber1][
                        hypernyms1[len(hypernyms1) - 1]
                    ]
                    triple2 = graphsLabelsToTriples[graphNumber2][
                        hypernyms2[len(hypernyms2) - 1]
                    ]
                    if (
                        isinstance(triple1[2], Literal)
                        and not triple1[2].language == "en"
                        or isinstance(triple2[2], Literal)
                        and not triple2[2].language == "en"
                        or relatedness == 0
                    ):
                        pass
                    else:
                        pair = (triple1, triple2)
                        pairDict[pair] = relatedness
            graphNumber2 = graphNumber2 + 1
        graphNumber1 = graphNumber1 + 1
    return dict(sorted(pairDict.items(), key=lambda x: x[1], reverse=True))


def dictTripleRelateness(dictTupleRelatenes: Dict[Tuple, float]) -> Dict[URIRef, float]:
    """
    Given dictionary with tuple of triples as a key and relatedness as value. Dictionary triple, his relatedness is returned.

    This function divides tuples to tripels and save it in dictionary triple-relatedness.
    --------------
    :param dictTupleRelatenes: dictionary tuple of triples with relatedness.
    :return: dictionary triple-relatedness.
    """
    dictTripleRelatenes: Dict[URIRef, float] = {}
    for tup in dictTupleRelatenes.keys():
        triple1 = tup[0]
        triple2 = tup[1]
        if triple1 not in dictTripleRelatenes:
            dictTripleRelatenes[triple1] = dictTupleRelatenes[tup]
        if triple2 not in dictTripleRelatenes:
            dictTripleRelatenes[triple2] = dictTupleRelatenes[tup]
    return dictTripleRelatenes


def getLabelsToTriples(graph: Graph) -> Dict[str, URIRef]:
    """
    Given a subgraph for entity. Dictionary Label,triple is returned.

    This function compute from every predicate string label and matches it to triple in dictionary.
    --------------
    :param graph: DBPedia subgraph for entity.
    :return: dictionary triple, label.
    """
    labels = {}
    for triple in graph:
        label = getLabel(triple)
        if label not in labels:
            labels[label] = triple
    return labels


def getLabel(triple: Tuple) -> str:
    """
    Given a RDF triple. Label of predicate as a string is returned.

    --------------
    :param triple: DBPedia RDF triple.
    :return: label string.
    """
    try:
        predicate = triple[1].n3()
        label = predicate.split("/")[-1][:-1]
    except IndexError:
        pass
    return label


def getHypernymsPerList(labels: List[str]) -> List[List[str]]:
    """
    Given list of labels string. List with list of hypernyms for every label is returned.

    --------------
    :param labels: list of strings.
    :return: list of list with hypernyms and label itself.
    """
    wordsHypernyms = []
    for label in labels:
        hypernyms = getHypernyms(label)
        hypernyms.append(label)
        wordsHypernyms.append(hypernyms)
    return wordsHypernyms


def getHypernyms(lable: str) -> List[str]:
    """
    Given label string. List of Hypernyms is returned.

    --------------
    :param lable: string.
    :return: list of hypernyms to this label.
    """
    listHypernyms = []
    with suppress(Exception):
        hypernyms = wordnet.synset(lable + ".n.01").hypernyms()
        for hypernym in hypernyms:
            listHypernyms.append(hypernym.lemma_names()[0])
    return listHypernyms


def calculateRelatedness(hypernyms1: List[str], hypernyms2: List[str]) -> float:
    """
    Given two words. Relatedness score is returned.

    --------------
    :param hypernyms1: list of strings.
    :param hypernyms2: list of strings.
    :return: relatedness score.
    """
    intersectionList = [value for value in hypernyms1 if value in hypernyms2]
    intersectionCount = len(intersectionList)
    UnionCount = len(set(hypernyms1) | set(hypernyms2))

    return intersectionCount / UnionCount


def main() -> None:
    """Call ."graphs_for_the_question(entities) to get list of graphs. calclualteRelatenessOfGraphs(graphs) for get dictionary triple relatedness."""
    # entities = [
    #    rdflib.term.URIRef("http://dbpedia.org/resource/Vladimir_Putin"),
    #    rdflib.term.URIRef("http://dbpedia.org/resource/Donald_Trump"),
    # ]
    # graphs = graphs_for_the_question(entities)
    # tupleRelatedness = calclualteRelatenessOfGraphs(graphs)
    # tripleRelatedness = dictTripleRelateness(tupleRelatedness)
    # i = 0
    # for p in tripleRelatedness:
    #    i = i + 1
    #    print(p, tripleRelatedness[p])
    #    print("\n")
    # print(i)


# Call from shell as main.
if __name__ == "__main__":
    # start_time = time.time()
    main()
    # print(time.time() - start_time)
