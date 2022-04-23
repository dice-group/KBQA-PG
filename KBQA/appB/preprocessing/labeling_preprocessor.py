"""Preprocess data."""
import json
import math
import os
import pickle
import re
from tqdm import tqdm
from pathlib import Path
import distance
from difflib import ndiff

from typing import Union
from typing import Callable

from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper import JSON

from KBQA.appB.summarizers.utils import query_dbspotlight

from KBQA.appB.preprocessing import utils
from KBQA.appB.preprocessing.utils import separate_qtq_file
from KBQA.appB.preprocessing.utils import preprocess_file
from KBQA.appB.preprocessing.utils import preprocess_natural_language_file
from KBQA.appB.preprocessing.utils import preprocess_natural_language_sentence
from KBQA.appB.preprocessing.utils import do_valid_preprocessing
from KBQA.appB.preprocessing.utils import upper_bound_literal
from KBQA.appB.preprocessing.utils import do_replacements
from KBQA.appB.preprocessing.utils import revert_replacements
from KBQA.appB.preprocessing.utils import encode_asterisk
from KBQA.appB.preprocessing.utils import decode_asterisk
from KBQA.appB.preprocessing.utils import encode_datatype
from KBQA.appB.preprocessing.utils import decode_datatype
from KBQA.appB.preprocessing.utils import uri_to_prefix

SPARQL_WRAPPER = utils.SPARQL_WRAPPER
PREFIX_EQUIVALENTS = utils.PREFIX_EQUIVALENTS
SPARQL_KEYWORDS = utils.SPARQL_KEYWORDS
VALID_SPARQL_REPLACEMENTS = utils.VALID_SPARQL_REPLACEMENTS
ENCODING_REPLACEMENTS = utils.ENCODING_REPLACEMENTS
IRI_SCHEMES = utils.IRI_SCHEMES
PREFIX_EXCEPTIONS = utils.PREFIX_EXCEPTIONS
PREFIX_TO_URI = utils.PREFIX_TO_URI
URI_TO_PREFIX = utils.URI_TO_PREFIX
HTTPS_URI_TO_PREFIX = utils.HTTPS_URI_TO_PREFIX


def preprocess_qtq_file(input_file_path: Union[str, os.PathLike, Path],
                        output_folder_path: Union[str, os.PathLike, Path] = Path("preprocessed_data_files"),
                        keep_separated_input_file: bool = False,
                        separated_input_files_folder_path: Union[str, os.PathLike, Path] =
                        Path("separated_data_files"),
                        checkpointing_period: int = 10) -> tuple[Path, Path, Path]:
    """Separate and preprocess a JSON qtq-file into three files, question-, triple-, sparql-file.

    Let file_name_without_json be the file_name without the trailing ".json".
    Store the preprocessed questions in <output_folder_path>/<file_name_without_json>.en.
    Store the preprocessed triples in <output_folder_path>/<file_name without_json>.triple.
    Store the preprocessed SPARQL queries in <output_folder_path>/<file_name_without_json>.sparql.

    Also applies filter_triples() on the triples of the qtq-file.

    Args:
        input_file_path: The qtq-file-path. Must be a valid JSON with suffix ".json".
        output_folder_path: The folder-path where the preprocessed files are stored.
        keep_separated_input_file: If True, store the separated qtq-file in separated_input_files_folder_path.
        separated_input_files_folder_path: The input-file is separated into questions, triples and SPARQLs before
                                           preprocessing. This is folder-path where these intermediate files are stored.
        checkpointing_period: For every checkpointing_period of processed examples, the examples are stored in
                              <output_file_path>.checkpoint_data and the algorithm state in
                              <checkpoint_data>.checkpoint_state. If the algorithm is interrupted, it can be resumed
                              from the checkpoint by calling it with the same arguments.

    Note:
        Checkpointing is not applied on the data-separation step.
    """
    input_file_path = Path(input_file_path)
    output_folder_path = Path(output_folder_path)
    separated_input_files_folder_path = Path(separated_input_files_folder_path)
    if input_file_path.suffix != ".json":
        raise ValueError("input_file_path should be ending with \".json\"")
    output_folder_path.mkdir(parents=True, exist_ok=True)
    natural_language_file_path, triples_file_path, sparql_file_path = separate_qtq_file(
        input_file_path=input_file_path, output_folder_path=separated_input_files_folder_path)
    preprocessed_natural_language_file_path = output_folder_path / input_file_path.with_suffix(".en").name
    preprocessed_triples_file_path = output_folder_path / input_file_path.with_suffix(".triple").name
    preprocessed_sparql_file_path = output_folder_path / input_file_path.with_suffix(".sparql").name
    preprocessed_natural_language_file_path = preprocess_natural_language_file(
        input_file_path=natural_language_file_path, output_file_path=preprocessed_natural_language_file_path,
        checkpointing_period=checkpointing_period)
    preprocessed_triples_file_path = preprocess_triples_file(input_file_path=triples_file_path,
                                                             output_file_path=preprocessed_triples_file_path,
                                                             checkpointing_period=checkpointing_period)
    preprocessed_sparql_file_path = preprocess_sparql_file(input_file_path=sparql_file_path,
                                                           output_file_path=preprocessed_sparql_file_path,
                                                           checkpointing_period=checkpointing_period)
    if not keep_separated_input_file:
        natural_language_file_path.unlink()
        triples_file_path.unlink()
        sparql_file_path.unlink()
        if not any(separated_input_files_folder_path.iterdir()):
            separated_input_files_folder_path.rmdir()
    return preprocessed_natural_language_file_path, preprocessed_triples_file_path, preprocessed_sparql_file_path


def preprocess_sparql_file(input_file_path: Union[str, os.PathLike, Path],
                           output_file_path: Union[str, os.PathLike, Path, None] = None,
                           checkpointing_period: int = 10) -> Path:
    """Preprocess a SPARQL file.

    Args:
        input_file_path: The path of the file to preprocess.
        output_file_path: The path of the final preprocessed file. The file is created if it does not exist or
                          overwritten if it already exists. If None, defaults to
                          "preprocessed_data_files/<input_file_name>" where <input_file_name> is the name of the
                          input-file.
        checkpointing_period: For every checkpointing_period of processed examples, the examples are stored in
                              <output_file_path>.checkpoint_data and the algorithm state in
                              <checkpoint_data>.checkpoint_state. If the algorithm is interrupted, it can be resumed
                              from the checkpoint by calling it with the same arguments.
    Returns:
        The path of the preprocessed file.
    """
    output_file_path = preprocess_file(preprocessing_function=preprocess_sparql, input_file_path=input_file_path,
                                       output_file_path=output_file_path, checkpointing_period=checkpointing_period,
                                       progress_bar_description="Amount of preprocessed SPARQLs",
                                       progress_bar_unit="SPARQL")
    return output_file_path


def preprocess_sparql(s):
    s = do_valid_preprocessing(s)
    s = encode(s)
    s = s.strip()
    s = re.sub(r" +", " ", s)
    return s


def preprocess_triples_file(input_file_path: Union[str, os.PathLike, Path],
                            output_file_path: Union[str, os.PathLike, Path, None] = None,
                            checkpointing_period: int = 10) -> Path:
    """Preprocess a triples file.

    Args:
        input_file_path: The path of the file to preprocess.
        output_file_path: The path of the final preprocessed file. The file is created if it does not exist or
                          overwritten if it already exists. If None, defaults to
                          "preprocessed_data_files/<input_file_name>" where <input_file_name> is the name of the
                          input-file.
        checkpointing_period: For every checkpointing_period of processed examples, the examples are stored in
                              <output_file_path>.checkpoint_data and the algorithm state in
                              <checkpoint_data>.checkpoint_state. If the algorithm is interrupted, it can be resumed
                              from the checkpoint by calling it with the same arguments.
    Returns:
        The path of the preprocessed file.
    """
    output_file_path = preprocess_file(preprocessing_function=preprocess_triples, input_file_path=input_file_path,
                                       output_file_path=output_file_path, checkpointing_period=checkpointing_period,
                                       progress_bar_description="Amount of preprocessed triple-sets",
                                       progress_bar_unit="triple-set")
    return output_file_path


def preprocess_triples(triples_example):
    s = triples_example
    s = upper_bound_literal(s)  # Max six long words.
    s = preprocess_sparql(s)
    return s


def encode(sparql):
    """Encode sparql.

    sparql will not be a valid SPARQL query afterwards and has to be decoded by decode() to make it valid again.
    """
    s = sparql
    s = do_replacements(s, ENCODING_REPLACEMENTS)
    s = encode_asterisk(s)
    s = encode_datatype(s)
    s = encode_uri_by_label(s)
    s = s.strip()
    s = re.sub(r" +", " ", s)
    return s


def decode(encoded_sparql):
    """"Decode encoded sparql to make it a valid sparql query again."""
    s = encoded_sparql
    s = decode_label_by_uri(s)
    s = decode_datatype(s)
    s = decode_asterisk(s)
    s = revert_replacements(s, ENCODING_REPLACEMENTS, remove_successive_whitespaces=False)
    s = s.strip()
    s = re.sub(r" +", " ", s)
    return s


def decode_file(file):
    """Decode a file of encoded SPARQLs."""
    with open(file) as f:
        encoded_sparqls = [decode(line) for line in f]

    return encoded_sparqls


def encode_uri_by_label(s):
    """Replace "<prefix:><path>" by "<prefix:> <label_of_the_corresponding_URI> :end_label".

    ":end_label" should be part of the tokenizer vocabulary.
    Excluded prefixes are: "xsd:" and PREFIX_EXCEPTIONS.

    Args:
        s: String where the encoding is done.

    Returns:
        String after encoding.
    """
    excluded = ["xsd:"]
    for row in PREFIX_EXCEPTIONS:
        exception = row[0]
        excluded.append(exception)
    prefixes = list(PREFIX_TO_URI.keys())
    prefixes = [elem for elem in prefixes if elem not in excluded]
    for prefix in prefixes:
        s = re.sub(f"(?!(<))\\b({prefix})(([^\\s.,;]|(\\.[^\\s,;]))*)", generate_label_encoding, s)
    s = re.sub(r" +", " ", s)
    return s


def generate_label_encoding(match):
    """Generates the string for "<prefix:><path>"  which is "<prefix:> <label_of_the_corresponding_URI> :end_label".

    Only supports english labels, i.e. "<label>"@en.

    Args:
        match: A re.Match object.
    Returns:
        string: "<prefix:> <label_of_the_corresponding_URI> :end_label" if a label was found.
                "<prefix:><path>" else.
    """
    prefix = match.group(2)
    path = match.group(3)
    label = None

    uri = '<' + PREFIX_TO_URI[prefix] + path + '>'
    query = f"""SELECT DISTINCT ?label WHERE
        {{
            {uri} rdfs:label ?label
            FILTER(langMATCHES(LANG(?label), "en"))
        }}
        """
    SPARQL_WRAPPER.setQuery(query)
    try:
        answer = SPARQL_WRAPPER.queryAndConvert()
    except BaseException:
        print(f"An exception occurred at query:\n{query}")
        raise
    results = answer["results"]["bindings"]
    if len(results) > 0:
        label = results[0]["label"]["value"]

    if label is None:
        return prefix + path
    return prefix + ' ' + label + " :end_label "


def decode_label_by_uri(s):
    """Replace "<prefix:> <label_of_the_corresponding_URI> :end_label" by "<prefix:><path>".

    ":end_label" should be part of the tokenizer vocabulary.
    """
    initial_s = s
    s = decode_label_with_mapping(s)
    s = decode_label_with_entity_linking(s, context=initial_s)
    return s


def decode_label_with_mapping(s: str) -> str:
    """Replace a label with a uri from mapping the label back to the corresponding entity in DBpedia.

    Replace "<prefix:> <label_of_the_corresponding_URI> :end_label" by "<prefix:><path>".
    Excluded prefixes are: "xsd:" and PREFIX_EXCEPTIONS.

    Args:
        s: The string where labels should be decoded.

    Returns:
        A string with decoded labels if some were found.
    """
    excluded = ["xsd:"]
    for row in PREFIX_EXCEPTIONS:
        exception = row[0]
        excluded.append(exception)
    prefixes = list(PREFIX_TO_URI.keys())
    prefixes = [elem for elem in prefixes if elem not in excluded]
    prefixes_regex = '|'.join(prefixes)
    s = re.sub(f"(?!(<))\\b({prefixes_regex})((?!{prefixes_regex})|(.(?!{prefixes_regex}))*?):end_label",
               generate_label_decoding, s)
    return s


def generate_label_decoding(match):
    """Generates the string for "<prefix:> <label_of_the_corresponding_URI> :end_label" which is "<prefix:><path>".

    Only supports english labels, i.e. "<label>"@en.

    Args:
        match: A re.Match object.
    Returns:
        string: Some "<prefix:><path>" if a uri is found. Else an empty string "".
    """
    prefix = match.group(2)
    label = match.group(3).strip()
    uri = None

    query = f"""SELECT DISTINCT ?uri WHERE
        {{
            ?uri rdfs:label "{label}"@en
            FILTER(strstarts(str(?uri), str({prefix})))
        }}
        """
    SPARQL_WRAPPER.setQuery(query)
    try:
        response = SPARQL_WRAPPER.queryAndConvert()
    except BaseException:
        print(f"An exception occurred at query:\n{query}")
        raise
    bindings = response["results"]["bindings"]
    if len(bindings) > 0:
        uri = bindings[0]["uri"]["value"]

    if uri is None:
        whole_match = match.group(0)
        return whole_match
    prefix_uri = uri_to_prefix("<" + uri + ">")
    return prefix_uri


def decode_label_with_entity_linking(s: str, context: str) -> str:
    """Replace a label with a uri found by entity recognition on the label.

    Replace "<prefix:> <label_of_the_corresponding_URI> :end_label" by "<prefix:><path>".
    Excluded prefixes are: "xsd:" and PREFIX_EXCEPTIONS.

    Args:
        s: The string where labels should be decoded.
        context: The string where entities are recognized and then linked to some uri. If a recognized entity is
                 the same as a label in s, it is replaced by the corresponding uri.

    Returns:
        A string with decoded labels if some were found.
    """
    excluded = ["xsd:"]
    for row in PREFIX_EXCEPTIONS:
        exception = row[0]
        excluded.append(exception)
    response = query_dbspotlight(context, confidence=0.1)
    if "Resources" not in response:
        resources = list()
    else:
        resources = response["Resources"]
    text_to_uri = dict()
    for linked_entity in resources:
        if "@URI" in linked_entity and "@surfaceForm" in linked_entity:
            text_to_uri[linked_entity["@surfaceForm"]] = linked_entity["@URI"]
    prefixes = list(PREFIX_TO_URI.keys())
    prefixes = [elem for elem in prefixes if elem not in excluded]
    prefixes_regex = '|'.join(prefixes)
    for match in \
            re.finditer(f"(?!(<))\\b(({prefixes_regex})((?!{prefixes_regex})|(.(?!{prefixes_regex}))*?)):end_label", s):
        whole_match = match.group(0)
        prefix_label = match.group(2).strip()
        label = match.group(4).strip()
        if label in text_to_uri:
            s = re.sub(whole_match, '<' + text_to_uri[label] + '>', s)
        elif prefix_label in text_to_uri:
            s = re.sub(whole_match, '<' + text_to_uri[prefix_label] + '>', s)
    s = uri_to_prefix(s)
    return s


def sparql_encoder_levenshtein_dist_on_file(input_file_path: Union[str, os.PathLike, Path],
                                            log_lower_bound: float = math.inf) -> float:
    """Preprocess the given data and then calculate the Levenshtein distance between encoding and decoding it.

    The SPARQL preprocessing part is applied for preprocessing.

    Args:
        input_file_path: A path-like object to the file with the SPARQLs.
        log_lower_bound: Print logging information to stdout for each example which has an equal or higher Levenshtein
                         distance than log_lower_bound.

    Returns:
        The mean Levenshtein distance.
    """
    input_file_path = Path(input_file_path)
    cumulative_dist = 0
    amount = 0
    with open(input_file_path, "r", encoding="utf-8") as file:
        for sparql in tqdm(file, desc="Amount of scored SPARQLs", unit="SPARQL"):
            dist = sparql_encoder_levenshtein_dist(sparql.strip(), log_lower_bound=log_lower_bound)
            cumulative_dist += dist
            amount += 1
    mean_dist = cumulative_dist / amount
    return mean_dist


def sparql_encoder_levenshtein_dist(sparql: str, log_lower_bound: float = math.inf) -> float:
    """Preprocess sparql and then calculate the Levenshtein distance between encoding and decoding it.

    The SPARQL preprocessing part is applied for preprocessing.

    Args:
        sparql: A SPARQL string.
        log_lower_bound: Print logging information to stdout for each example which has an equal or higher Levenshtein
                         distance than log_lower_bound.

    Returns:
        The Levenshtein distance.
    """
    preprocessed = do_valid_preprocessing(sparql)
    encoded = encode(preprocessed)
    decoded = decode(encoded)
    dist = distance.levenshtein(preprocessed, decoded)
    if dist >= log_lower_bound:
        print("\n--------------------------------------------------")
        print(f"SPARQL: {sparql}")
        print(f"\nPreprocessed: {preprocessed}")
        print(f"\nEncoded: {encoded}")
        print(f"\nDecoded: {decoded}")
        print(f"\nDifference:\n")
        diff = ndiff(preprocessed.split(), decoded.split())
        print('\n'.join(diff))
        print(f"\nDistance: {dist}")
        print("----------------------------------------------------")
    return dist
