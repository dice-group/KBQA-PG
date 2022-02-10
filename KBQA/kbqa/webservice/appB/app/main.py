"""Main module for the application logic of approach B."""
import json
from typing import Any
from typing import Dict
from typing import List

from app.arguments.args_summarizer import ONE_HOP_RANK_SUMMARIZER
from app.bert_wordpiece_spbert.run import run
from app.postprocessing.postprocessing import postprocessing
from app.preprocessing.preprocessing_qtq import preprocessing_qtq
from app.preprocessing.seperate_qtq import seperate_qtq
from app.qald_builder import qald_builder
from app.qald_builder import qald_builder_empty_answer
from app.summarizer.one_hop_rank_summarizer import OneHopRankSummarizer
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException


print("Loading summarizer...")
ohrs = OneHopRankSummarizer(
    ONE_HOP_RANK_SUMMARIZER.lower_rank,
    ONE_HOP_RANK_SUMMARIZER.max_triples,
    ONE_HOP_RANK_SUMMARIZER.limit,
    ONE_HOP_RANK_SUMMARIZER.timeout,
)


def main(query: str, lang: str = "en") -> Dict[str, Any]:
    """Start main method of the application logic for approach A.

    Process the query, which contains the question asked by an enduser and an
    optional language tag.

    Parameters
    ----------
    query : str
        Natural language question asked by an enduser.
    lang : str, optional
        Language tag (default is "en", i.e. an english question is asked).

    Returns
    -------
    answer_qald : dict
        Answers for the given question formatted in the QALD-format.
    """
    print("Question:", query.encode("utf-8"))

    query_pairs = pipeline_for_bert_wordpiece_spbert(query)
    sparql_query = query_pairs["0"]

    answer_qald = ask_dbpedia(query, sparql_query, lang)

    return answer_qald


def ask_dbpedia(question: str, sparql_query: str, lang: str) -> Dict[str, Any]:
    """Send a SPARQL-query to DBpedia and return a formated QALD-string containing the answers.

    Parameters
    ----------
    question : str
        Natural language question asked by an enduser.
    sparql_query : str
        SPARQL-query to be sent to DBpedia. Should correspond to the question.
    lang : str
        Language tag for the question (should always be "en").

    Returns
    -------
    qald_answer : str
        Formated string in the QALD-format containing the answers for the sparql_query.
    """
    print("SPARQL-Query:", sparql_query.encode("utf-8"))

    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(sparql_query)
        answer = sparql.query().convert()
    except SPARQLWrapperException as exception:
        print("SPARQLWrapperException", exception)

        qald_answer = qald_builder_empty_answer("", question, lang)

        return qald_answer

    if len(answer["results"]["bindings"]) == 0:
        qald_answer = qald_builder_empty_answer(sparql_query, question, lang)
    else:
        qald_answer = qald_builder(sparql_query, answer, question, lang)

    return qald_answer


def pipeline_for_bert_wordpiece_spbert(question: str) -> Dict[str, str]:
    """Pipeline for approach B using BERT_wordpiece_SPBERT.

    Given a natural language question, the pipeline contains the following steps:
    1. Create a subgraph based on recognized entities and trained predicates.
    2. Create a QTQ dataset based on the summarized subgraph.
    3. Preprocess the QTQ dataset s.t. SPBert can work with it
    4. Predict a SPARQL-query for the question using SPBert.
    5. Postprocess the predicted query into a valid SPARQL-query

    Parameters
    ----------
    question : str
        Natural language question asked by an enduser.

    Returns
    -------
    result : dict
        Dictionary containing the predicted SPARQL-query at the key "0".
    """
    # summarizer
    summarize(question)

    # preprocessing
    seperate_qtq()
    preprocessing_qtq()

    # predicting
    run()

    # postprocessing
    result = postprocessing()

    return result


def summarize(question: str) -> None:
    """Create a subgraph using a summarizer and store it a QTQ-dataset.

    Parameters
    ----------
    question : str
        Natural language question asked by an enduser.
    """
    summarized_triples = ohrs.summarize(question)

    save_summarized_result(question, "", summarized_triples)


def save_summarized_result(question: str, sparql: str, triples: str) -> None:
    """Save the summarized results in a QTQ dataset.

    Parameters
    ----------
    question : str
        Natural language question.
    sparql : str
        SPARQL-query (since we have to predict the query, this should be empty).
    triples : str
        List of triples in the format <subject> <predicate> <object>.
    """
    path = "app/data/input/question.json"

    dataset: Dict[str, List[Dict]] = {"questions": list()}

    qtq = dict()
    qtq["question"] = question
    qtq["query"] = sparql
    qtq["triples"] = triples
    dataset["questions"].append(qtq)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=4, separators=(",", ": "))
