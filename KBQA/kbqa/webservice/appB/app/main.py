"""Main module for the application logic of approach B."""
from configparser import ConfigParser
from configparser import SectionProxy
import json
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from app.base_pipeline import BasePipeline
from app.preprocessing import QTQ_DATA_DIR
from app.preprocessing import SPLIT_NAME
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

    sparql_query = pipeline_.predict_sparql_query(query)
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
    if summarizer_ is None:
        summarized_triples = list()
    else:
        summarized_triples = summarizer_.summarize(question)

    data_dir = QTQ_DATA_DIR

    if os.path.exists(data_dir) is False:
        os.makedirs(data_dir)

    filename = f"{SPLIT_NAME}.json"

    dataset: Dict[str, List[Dict[str, Any]]] = {"questions": list()}

    qtq: Dict[str, Any] = dict()
    qtq["question"] = question
    qtq["query"] = ""
    qtq["triples"] = summarized_triples
    dataset["questions"].append(qtq)

    with open(f"{data_dir}/{filename}", "w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=4, separators=(",", ": "))


def load_config(path: str) -> Tuple[Union[BaseSummarizer, None], BasePipeline]:
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
        Initialized summarizer specified in the 'general' section. If the
        attribute is set to 'None', None will be returned.

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
    elif summarizer_name == "one_hop":
        pass  # TODO
    elif summarizer_name == "lauren":
        smrzr = init_lauren_summarizer(parser["lauren"])
    elif summarizer_name == "gold":
        smrzr = init_gold_summarizer(parser["gold"])
    elif summarizer_name == "None":
        smrzr = None
        print("WARNING: Summarizer is set to 'None'. Summarizing will be skipped.")
    else:
        raise ValueError(f"Summarizer {summarizer_name} is not supported.")

    if architecture_name == "bert_spbert":
        pline = init_bert_spbert_pipeline(parser["bert_spbert"])
    elif architecture_name == "bert_spbert_spbert":
        pline = init_bert_spbert_spbert(parser["bert_spbert_spbert"])
    elif architecture_name == "knowbert_spbert_spbert":
        pline = init_knowbert_spbert_spbert(parser["knowbert_spbert_spbert"])
    elif architecture_name == "bert_triple-bert_spbert":
        pline = init_bert_triplebert_spbert(parser["bert_triple-bert_spbert"])
    elif architecture_name == "t5":
        pline = init_t5(parser["t5"])
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


def init_lauren_summarizer(section: SectionProxy) -> BaseSummarizer:
    """Initialize the LarenSummarizer with the given values in the config section.

    Parameters
    ----------
    section : SectionProxy
        Section from the configuration file with the corresponding dynamic
        attributes.

    Returns
    -------
    LaurenSummarizer
        Initialized instance of the LaurenSummarizer.
    """
    from app.summarizer.lauren_summarizer import LaurenSummarizer

    limit = int(section["limit"])

    lauren = LaurenSummarizer(limit=limit)

    return lauren


def init_gold_summarizer(section: SectionProxy) -> BaseSummarizer:
    """Initialize the GoldSummarizer with the given values in the config section.

    Parameters
    ----------
    section : SectionProxy
        Section from the configuration file with the corresponding dynamic
        attributes.

    Returns
    -------
    GoldSummarizer
        Initialized instance of the GoldSummarizer.
    """
    from app.summarizer.gold_summarizer import GoldSummarizer

    dataset = str(section["dataset"])

    gold = GoldSummarizer(dataset)

    return gold


def init_bert_spbert_pipeline(section: SectionProxy) -> BasePipeline:
    """Initialize the pipeline for BERT_SPBERT.

    Parameters
    ----------
    section : SectionProxy
        Section from the configuration file with the corresponding dynamic
        attributes.

    Returns
    -------
    BertSPBertPipeline
        Initialized BERT_SPBERT_SPBERT pipeline, which can be used to predict
        SPARQL queries using this architecture.
    """
    from app.namespaces import BERT_SPBERT
    from app.bert_spbert import BertSPBertPipeline

    parsed_section = parse_section(section)

    for entry, value in parsed_section:
        setattr(BERT_SPBERT, entry, value)

    bs_pipeline = BertSPBertPipeline(BERT_SPBERT)

    return bs_pipeline


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

    parsed_section = parse_section(section)

    for entry, value in parsed_section:
        setattr(BERT_SPBERT_SPBERT, entry, value)

    bss_pipeline = BertSPBertSPBertPipeline(BERT_SPBERT_SPBERT)

    return bss_pipeline


def init_knowbert_spbert_spbert(section: SectionProxy) -> BasePipeline:
    """Initialize the pipeline for KNOWBERT_SPBERT_SPBERT.

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
    from app.namespaces import KNOWBERT_SPBERT_SPBERT
    from app.knowbert_spbert_spbert import KnowBertSPBertSPBertPipeline

    parsed_section = parse_section(section)

    for entry, value in parsed_section:
        setattr(KNOWBERT_SPBERT_SPBERT, entry, value)

    kss_pipeline = KnowBertSPBertSPBertPipeline(KNOWBERT_SPBERT_SPBERT)

    return kss_pipeline


def init_bert_triplebert_spbert(section: SectionProxy) -> BasePipeline:
    """Initialize the pipeline for BERT_TRIPLE_BERT.

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
    from app.namespaces import BERT_TRIPLEBERT_SPBERT
    from app.bert_triplebert_spbert import BertTripleBertSPBertPipeline

    parsed_section = parse_section(section)

    for entry, value in parsed_section:
        setattr(BERT_TRIPLEBERT_SPBERT, entry, value)

    bts_pipeline = BertTripleBertSPBertPipeline(BERT_TRIPLEBERT_SPBERT)

    return bts_pipeline


def init_t5(section: SectionProxy) -> BasePipeline:
    """Initialize the pipeline for t5.

    Parameters
    ----------
    section : SectionProxy
        Section from the configuration file with the corresponding dynamic
        attributes.

    Returns
    -------
    T5Pipeline
        Initialized t5 pipeline, which can be used to predict
        SPARQL queries using this architecture.
    """
    from app.namespaces import T5
    from app.t5 import T5Pipeline

    parsed_section = parse_section(section)

    for entry, value in parsed_section:
        setattr(T5, entry, value)

    t5_pipeline = T5Pipeline(T5)

    return t5_pipeline


def parse_section(section: SectionProxy) -> List[Tuple[str, Union[int, float, str]]]:
    """Parse a section into a list of tuples.

    Given a section element from a .ini file with pairs entry = value, create a
    list with tuples (entry, value), where value is parsed to an int or float if
    possible.

    Parameters
    ----------
    section : SectionProxy
        Section element from a .ini file.

    Returns
    -------
    list
        List containing tuples of the form (entry, value).
    """
    result: List[Tuple[str, Union[int, float, str]]] = list()

    for entry in section:
        value = section[entry]

        if is_int(value):
            result.append((entry, int(value)))
        elif is_float(value):
            result.append((entry, float(value)))
        else:
            result.append((entry, str(value)))

    return result


def is_int(value: str) -> bool:
    """Check, whether a string can be parsed into an int.

    Parameters
    ----------
    value : str
        String to be checked.

    Returns
    -------
    bool
        True, if value can be parsed to an int, else False.
    """
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_float(value: str) -> bool:
    """Check, whether a string can be parsed into a float.

    Parameters
    ----------
    value : str
        String to be checked.

    Returns
    -------
    bool
        True, if value can be parsed to an float, else False.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


summarizer_, pipeline_ = load_config(config_path)
