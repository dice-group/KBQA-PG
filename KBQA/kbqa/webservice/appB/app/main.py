"""Main module for the application logic of approach B."""
from configparser import ConfigParser
from configparser import SectionProxy
import json
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from app.base_pipeline import BasePipeline
from app.preprocessing import preprocessing_qtq
from app.preprocessing import SEPERATE_QTQ
from app.preprocessing import seperate_qtq
from app.qald_builder import qald_builder_ask_answer
from app.qald_builder import qald_builder_empty_answer
from app.qald_builder import qald_builder_select_answer
from app.summarizer import BaseSummarizer
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException

config_path = "/config/app_b_config.ini"


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

    summarize(query)

    seperate_qtq()
    preprocessing_qtq()

    sparql_query = main_pipeline.predict_sparql_query(query)
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

    if "results" in dict(answer):
        # SELECT queries
        if len(answer["results"]["bindings"]) == 0:
            qald_answer = qald_builder_empty_answer(sparql_query, question, lang)
        else:
            qald_answer = qald_builder_select_answer(
                sparql_query, answer, question, lang
            )
    elif "boolean" in dict(answer):
        # ASK queries
        qald_answer = qald_builder_ask_answer(sparql_query, answer, question, lang)
    else:
        print("No results and boolean found.")
        qald_answer = qald_builder_empty_answer("", question, lang)

    return qald_answer


def summarize(question: str) -> None:
    """Summarize a subgraph and store the resulting triples in a qtq-file.

    Parameters
    ----------
    question : str
        Natural language question.
    """
    summarized_triples = main_summarizer.summarize(question)

    data_dir = SEPERATE_QTQ.data_dir

    if os.path.exists(data_dir) is False:
        os.makedirs(data_dir)

    filename = f"{SEPERATE_QTQ.subset}.json"

    dataset: Dict[str, List[Dict[str, Any]]] = {"questions": list()}

    qtq: Dict[str, Any] = dict()
    qtq["question"] = question
    qtq["query"] = ""
    qtq["triples"] = summarized_triples
    dataset["questions"].append(qtq)

    with open(f"{data_dir}/{filename}", "w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=4, separators=(",", ": "))


def load_config(path: str) -> Tuple[BaseSummarizer, BasePipeline]:
    """Load the config file for all configurations.

    The config file is expected to be an .ini file, which contains
    a section 'general' with the attributes 'summarizer' and 'architecture'.
    The values of those attributes should have there own section with all
    dynamic parameters, which are used to initialize the corresponding
    archtecture.

    Parameters
    ----------
    path : str
        Path to the .ini configuration file.

    Returns
    -------
    BaseSummarizer
        Initialized summarizer specified in the 'general' section.

    BasePipeline
        Initialized pipeline for the specified architecture.

    Raises
    ------
    ValueError
        If a section is not specified or the values are not supported.
    """
    parser = ConfigParser()

    parser.read(path)

    if "general" in parser.sections():
        general = parser["general"]

        summarizer_name = general["summarizer"]
        architecture_name = general["architecture"]
    else:
        raise ValueError("Config file does not contain section 'general'.")

    if summarizer_name == "one_hop_rank":
        smrzr = init_one_hop_rank_summarizer(parser["one_hop_rank"])
    else:
        raise ValueError(f"Summarizer {summarizer_name} is not supported.")

    if architecture_name == "bert_spbert_spbert":
        pline = init_bert_spbert_spbert(parser["bert_spbert_spbert"])
    # elif architecture_name == "bert_triple-bert_spbert":
    #     pline = init_bert_triplebert_spbert(parser["bert_triple-bert_spbert"])
    else:
        raise ValueError(f"Architecture {architecture_name} is not supported.")

    return smrzr, pline


def init_one_hop_rank_summarizer(section: SectionProxy) -> BaseSummarizer:
    """Initialize the OneHopRankSummarizer with the given values in the config section.

    Parameters
    ----------
    section : SectionProxy
        Section from the configuration file with the corresponding dynamic
        attributes.

    Returns
    -------
    OneHopRankSummarizer
        Initialized instance of the OneHopRankSummarizer.
    """
    from app.summarizer.one_hop_rank_summarizer import OneHopRankSummarizer

    datasets = str(section["datasets"])
    confidence = float(section["confidence"])
    lower_rank = int(section["lower_rank"])
    max_triples = int(section["max_triples"])
    limit = int(section["limit"])
    timeout = float(section["timeout"])

    ohrs = OneHopRankSummarizer(
        datasets=datasets,
        confidence=confidence,
        lower_rank=lower_rank,
        max_triples=max_triples,
        limit=limit,
        timeout=timeout,
    )

    return ohrs


def init_bert_spbert_spbert(section: SectionProxy) -> BasePipeline:
    """Initialize the pipeline for BERT_SPBERT_SPBERT.

    Parameters
    ----------
    section : SectionProxy
        Section from the configuration file with the corresponding dynamic
        attributes.

    Returns
    -------
    BertSPBertSPBertPipeline
        Initialized BERT_SPBERT_SPBERT pipeline, which can be used to predict
        SPARQL queries using this architecture.
    """
    from app.namespaces import BERT_SPBERT_SPBERT
    from app.bert_spbert_spbert import BertSPBertSPBertPipeline

    model_name = section["model_name"]

    BERT_SPBERT_SPBERT.load_model_path = f"/models/{model_name}"
    BERT_SPBERT_SPBERT.max_source_length = int(section["max_source_length"])
    BERT_SPBERT_SPBERT.max_triples_length = int(section["max_triples_length"])
    BERT_SPBERT_SPBERT.max_target_length = int(section["max_target_length"])

    bss_pipeline = BertSPBertSPBertPipeline(BERT_SPBERT_SPBERT)

    return bss_pipeline


# def init_bert_triplebert_spbert(section):
#     pass


main_summarizer, main_pipeline = load_config(config_path)
