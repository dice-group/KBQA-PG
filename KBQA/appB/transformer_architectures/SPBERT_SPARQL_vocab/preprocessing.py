"""Preprocess data."""
import json
import os
import pickle
import re
from tqdm import tqdm
from pathlib import Path
import distance

from typing import Union
from typing import Callable

from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper import JSON

from entity_linking import query_dbspotlight

SPARQL_WRAPPER = SPARQLWrapper("http://dbpedia.org/sparql")
SPARQL_WRAPPER.setReturnFormat(JSON)

PREFIXES = {
    "dbo:": "http://dbpedia.org/ontology/",
    "dbp:": "http://dbpedia.org/property/",
    "dbc:": "http://dbpedia.org/resource/Category:",
    "dbr:": "http://dbpedia.org/resource/",
    "rdf:": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs:": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd:": "http://www.w3.org/2001/XMLSchema#",
    "dct:": "http://purl.org/dc/terms/",
    "dc:": "http://purl.org/dc/elements/1.1/",
    "georss:": "http://www.georss.org/georss/",
    "geo:": "http://www.opengis.net/ont/geosparql#",
    "geof:": "http://www.opengis.net/def/function/geosparql/",
    "bif:": "http://www.openlinksw.com/schemas/bif#",
    "foaf:": "http://xmlns.com/foaf/0.1/",
    "owl:": "http://www.w3.org/2002/07/owl#",
    "yago:": "http://dbpedia.org/class/yago/",
    "skos:": "http://www.w3.org/2004/02/skos/core#",
}
PREFIX_SUBSTITUTION = [
    ["onto:", "http://dbpedia.org/ontology/", "https://dbpedia.org/ontology/", "dbo:"],
    ["http://dbpedia.org/property/", "https://dbpedia.org/property/", "dbp:"],
    ["http://dbpedia.org/resource/Category:", "https://dbpedia.org/resource/Category:", "dbc:"],
    ["res:", "http://dbpedia.org/resource/", "https://dbpedia.org/resource/", "dbr:"],
    ["http://www.w3.org/1999/02/22-rdf-syntax-ns#", "https://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:"],
    ["http://www.w3.org/2000/01/rdf-schema#", "https://www.w3.org/2000/01/rdf-schema#", "rdfs:"],
    ["http://www.w3.org/2001/XMLSchema#", "https://www.w3.org/2001/XMLSchema#", "xsd:"],
    ["http://purl.org/dc/terms/", "https://purl.org/dc/terms/", "dct:"],
    ["http://purl.org/dc/elements/1.1/", "https://purl.org/dc/elements/1.1/", "dc:"],
    ["http://www.georss.org/georss/", "https://www.georss.org/georss/", "georss:"],
    ["http://www.opengis.net/ont/geosparql#", "https://www.opengis.net/ont/geosparql#", "ogcgs:"],
    ["http://www.opengis.net/def/function/geosparql/", "https://www.opengis.net/def/function/geosparql/", "ogcgsf:"],
    ["http://www.openlinksw.com/schemas/bif#", "https://www.openlinksw.com/schemas/bif#", "bif:"],
    ["http://xmlns.com/foaf/0.1/", "https://xmlns.com/foaf/0.1/", "foaf:"],
    ["http://www.w3.org/2002/07/owl#", "https://www.w3.org/2002/07/owl#", "owl:"],
    ["http://dbpedia.org/class/yago/", "https://dbpedia.org/class/yago/", "yago:"],
    ["http://www.w3.org/2004/02/skos/core#", "https://www.w3.org/2004/02/skos/core#", "skos:"]
]
SPARQL_KEYWORDS = {
    "SELECT",
    "CONSTRUCT",
    "ASK",
    "DESCRIBE",
    "BIND",
    "WHERE",
    "LIMIT",
    "VALUES",
    "DISTINCT",
    "AS",
    "FILTER",
    "ORDER",
    "BY",
    "SERVICE",
    "OFFSET",
    "NOT",
    "EXISTS",
    "OPTIONAL",
    "UNION",
    "FROM",
    "GRAPH",
    "NAMED",
    "DESC",
    "ASC",
    "REDUCED",
    "STR",
    "LANG",
    "LANGMATCHES",
    "REGEX",
    "BOUND",
    "DATATYPE",
    "ISBLANK",
    "ISLITERAL",
    "ISIRI",
    "ISURI",
    "GROUP_CONCAT",
    "GROUP",
    "DELETE",
    "CLEAR",
    "CREATE",
    "COPY",
    "DROP",
    "INSERT",
    "LOAD",
    "DATA",
    "INTO",
    "WITH",
    "ALL",
    "SILENT",
    "DEFAULT",
    "USING",
    "MD5",
    "SHA1",
    "SHA256",
    "SHA384",
    "SHA512",
    "STRSTARTS",
    "STRENDS",
    "SAMETERM",
    "ISNUMERIC",
    "UCASE",
    "SUBSTR",
    "STRLEN",
    "STRBEFORE",
    "STRAFTER",
    "REPLACE",
    "LEVENSHTEIN_DIST",
    "LCASE",
    "ENCODE_FOR_URI",
    "CONTAINS",
    "CONCAT",
    "COALESCE",
    "CHOOSE_BY_MAX",
    "CHOOSE_BY_MIN",
    "YEAR",
    "DAY",
    "TZ",
    "TIMEZONE",
    "HOURS",
    "MINUTES",
    "MONTH",
    "NOW",
    "DUR_TO_USECS",
    "SECONDS_DBL",
    "USECS_TO_DUR",
    "IF",
    "MINUS",
    "AVG",
    "COUNT",
    "MAX",
    "MIN",
    "SAMPLE",
    "SUM",
    "ABS",
    "ADD",
    "BASE",
    "CEIL",
    "COS",
    "FLOOR",
    "HAMMING_DIST",
    "HAVERSINE_DIST",
    "LN",
    "LOG2",
    "MOD",
    "POWER",
    "RADIANS",
    "RAND",
    "ROUND",
    "ROUNDDOWN",
    "ROUNDUP",
    "TAN",
    "VAR",
    "VARP",
    "HAVING",
}
VALID_SPARQL_REPLACEMENTS = [
    ["rdf:type", 'a', 'a'],
    ['$', '?', '?'],  # Normalize to one variable symbol
    ['{', " { ", " { "],
    ['}', " } ", " } "],
]
ENCODING_REPLACEMENTS = [
    ['?', " variable: ", " ?"],
    [" * ", " all variables ", " * "],
    [" <= ", " less equal ", " <= "],
    [" >= ", " greater equal ", " >= "],
    [" != ", " not equal ", " != "],
    [" = ", " equal ", " = "],
    [" < ", " less than ", " < "],
    [" > ", " greater than ", " > "],
    ["||", " logical or ", " || "],
    ["&&", " logical and ", " && "],
    [" ! ", " logical not ", " ! "],
    ["@en", " language English ", "@en "],  # For now, we are only considering english literals.
    ["{", " bracket open", " { "],  # No space after " bracket open" to enable successive occurrences.
    ["}", " bracket close", " } "],
]


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


def separate_qtq_file(input_file_path: Union[str, os.PathLike, Path],
                      output_folder_path: Union[str, os.PathLike, Path] = "separated_data_files") \
        -> tuple[Path, Path, Path]:
    """Separate a JSON qtq-file into three files, question-, triple-, sparql-file.

    Let file_name_without_json be the file_name without the trailing ".json".
    Store the questions in <output_folder_path>/<file_name_without_json>.en.
    Store the triples in <output_folder_path>/<file_name without_json>.triple.
    Store the SPARQL queries in <output_folder_path>/<file_name_without_json>.sparql.

    Also applies filter_triples() on the triples of the qtq-file.

    Args:
        input_file_path: The path to the input file. Suffix must be ".json".
        output_folder_path: The path where the separated qtq-file parts should be stored.

    Returns:
        Tuple of (natural_language_file_path, triples_file_path, sparql_file_path).
    """
    input_file_path = Path(input_file_path)
    output_folder_path = Path(output_folder_path)
    if input_file_path.suffix != ".json":
        raise ValueError("input_file_path should be ending with \".json\"")
    output_folder_path.mkdir(parents=True, exist_ok=True)
    natural_language_file_path = output_folder_path / input_file_path.with_suffix(".en").name
    triples_file_path = output_folder_path / input_file_path.with_suffix(".triple").name
    sparql_file_path = output_folder_path / input_file_path.with_suffix(".sparql").name
    en_file = open(natural_language_file_path, "w", encoding="utf-8")
    triple_file = open(triples_file_path, "w", encoding="utf-8")
    sparql_file = open(sparql_file_path, "w", encoding="utf-8")
    input_file = open(input_file_path, "r", encoding="utf-8")
    data_json = json.load(input_file)
    for element in data_json["questions"]:
        en_file.write(element["question"] + "\n")
        sparql_file.write(element["query"] + "\n")
        if len(element["triples"]) == 0:
            triple_file.write('\n')
        else:
            triple_file.write(
                " . ".join(encode_new_line(element["triples"])) + " .\n")
    en_file.close()
    sparql_file.close()
    triple_file.close()
    input_file.close()
    return natural_language_file_path, triples_file_path, sparql_file_path


def encode_new_line(triples: list) -> list:
    """
    If a triple in triples has a '\n' character, replace it by ", ".

    Args:
        triples: list of triples.
    Returns:
        List of encoded triples.
    """
    return [triple.replace("\n", ", ") for triple in triples]


def preprocess_file(preprocessing_function: Callable[[str], str], input_file_path: Union[str, os.PathLike, Path],
                    output_file_path: Union[str, os.PathLike, Path, None] = None,
                    checkpointing_period: int = 10, progress_bar_description: Union[str, None] = None,
                    progress_bar_unit: str = "iteration") -> Path:
    """Preprocess a file with preprocessing_function.

    Args:
        preprocessing_function: This functions is applied to each line in the input-file at input_file_path. The result
                                is the respective line in the output-file at output_file_path.
        input_file_path: The path of the file to preprocess.
        output_file_path: The path of the final preprocessed file. The file is created if it does not exist or
                          overwritten if it already exists. If None, defaults to
                          "preprocessed_data_files/<input_file_name>" where <input_file_name> is the name of the
                          input-file.
        checkpointing_period: For every checkpointing_period of processed examples, the examples are stored in
                              <output_file_path>.checkpoint_data and the algorithm state in
                              <checkpoint_data>.checkpoint_state. If the algorithm is interrupted, it can be resumed
                              from the checkpoint by calling it with the same arguments.
        progress_bar_description: A str which is shown in front of the progress bar. Defaults to None which disables
                                  the description.
        progress_bar_unit: A str which is the unit of the progress bar. Defaults to "iteration".
    Returns:
        The path of the preprocessed file.
    """
    input_file_path = Path(input_file_path)
    if output_file_path is None:
        output_file_path = Path("preprocessed_data_files") / input_file_path.name
    else:
        output_file_path = Path(output_file_path)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_file_checkpoint_data_path = output_file_path.parent / (output_file_path.name + ".checkpoint_data")
    output_file_checkpoint_state_path = output_file_path.parent / (output_file_path.name + ".checkpoint_state")
    if output_file_checkpoint_state_path.exists():
        with open(output_file_checkpoint_state_path, "rb", encoding="utf-8") as state_file:
            num_stored_examples = pickle.load(state_file)
    else:
        num_stored_examples = 0
    with open(input_file_path, "r", encoding="utf-8") as input_file:
        with open(output_file_checkpoint_data_path, "a", encoding="utf-8") as checkpoint_file:
            for _ in range(num_stored_examples):
                input_file.readline()
            if num_stored_examples == 0:
                preprocessed_examples = ""
            else:
                preprocessed_examples = "\n"
            num_preprocessed_examples = 0
            for example in tqdm(input_file, desc=progress_bar_description, unit=progress_bar_unit,
                                initial=num_stored_examples):
                example = example.rstrip("\n")
                preprocessed_examples += preprocessing_function(example)
                preprocessed_examples += "\n"
                num_preprocessed_examples += 1
                if num_preprocessed_examples % checkpointing_period == 0:
                    preprocessed_examples = preprocessed_examples.removesuffix("\n")
                    checkpoint_file.write(preprocessed_examples)
                    checkpoint_file.flush()
                    num_stored_examples += num_preprocessed_examples
                    with open(output_file_checkpoint_state_path, "wb") as state_file:
                        pickle.dump(obj=num_stored_examples, file=state_file)
                    preprocessed_examples = "\n"
                    num_preprocessed_examples = 0
            preprocessed_examples = preprocessed_examples.rstrip("\n")
            checkpoint_file.write(preprocessed_examples)
            checkpoint_file.flush()
    output_file_checkpoint_data_path.replace(output_file_path)
    output_file_checkpoint_state_path.unlink(missing_ok=True)
    return output_file_path


def preprocess_natural_language_file(input_file_path: Union[str, os.PathLike, Path],
                                     output_file_path: Union[str, os.PathLike, Path, None] = None,
                                     checkpointing_period: int = 10) -> Path:
    """Preprocess a natural language file.

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
    output_file_path = preprocess_file(preprocessing_function=preprocess_natural_language_sentence,
                                       input_file_path=input_file_path, output_file_path=output_file_path,
                                       checkpointing_period=checkpointing_period,
                                       progress_bar_description="Amount of preprocessed questions",
                                       progress_bar_unit="question")
    return output_file_path


def preprocess_natural_language_sentence(w):
    w = re.sub(r" +", " ", w)
    w = w.strip()
    return w


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


def do_valid_preprocessing(s: str) -> str:
    """Preprocessing part which keeps the SPARQL s a valid sparql.

    Args:
        s: String which the preprocessing is done in.

    Returns:
        Preprocessed SPARQL with the same semantic as s.
    """
    s = inline_and_remove_prefixes(s)
    s = replace_single_to_double_quote(s)
    s = remove_zero_timezone(s)
    s = sparql_keyword_to_lower_case(s)
    s = uri_to_prefix(s)
    s = re.sub(r"@en", r"@en", s, flags=re.IGNORECASE)  # English language tag to lower case.
    s = do_replacements(s, VALID_SPARQL_REPLACEMENTS)
    return s


def replace_single_to_double_quote(s: str) -> str:
    """Replace single with double quote.

    Args:
        s: String which the replacement is done on.

    Returns:
        The string with replacements.
    """
    s = re.sub(r"(\B')", '"', s)
    s = re.sub(r"'([^_A-Za-z])", r'"\1', s)
    return s


def remove_zero_timezone(s: str) -> str:
    """Remove timezones with T00:00:00Z time.

    The SPBERT paper does it. It is not clear where such timezones occur, but it can not be harmful.

    Args:
        s: String where the removal is done.

    Returns:
        String with removed zero-timezone.
    """
    s = re.sub(r"(\d{4}-\d{2}-\d{2})T00:00:00Z", r"\1", s)
    return s


def inline_and_remove_prefixes(s: str) -> str:
    """Inline the prefixes of the SPARQL s and remove them.

    Args:
        s: SPARQL string.
    Returns:
        String with inlined and removed prefixes.
    """
    empty_prefix_name = False
    empty_prefix_uri = ""
    for pre_name, pre_url in re.findall(r"PREFIX\s([^:]*):\s<([^>]+)>", s):
        s = re.sub(f"PREFIX\\s{pre_name}:\\s<{pre_url}>", "", s)  # Remove prefix.
        if pre_name == "":
            empty_prefix_name = True
            empty_prefix_uri = pre_url
        else:
            s = re.sub(f"\\b{pre_name}:(\\S+)", f"<{pre_url}\\1>", s)  # Inline prefix.
        s = s.lstrip()
    if empty_prefix_name:
        # Empty prefix ':<something>' is replaced by its URI if it is preceded by a whitespace or a SPARQL term
        # delimiter ('.', ',', ';').
        s = re.sub(f"([.,;\\s]):(\\S+)", f"\\1<{empty_prefix_uri}\\2>", s)
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
    if triples_example == "":
        return ""
    triples_example = triples_example.rstrip(" .")
    triples = triples_example.split(" . ")
    preprocessed_triples = [preprocess_sparql(triple) for triple in triples]
    preprocessed_example = " . ".join(preprocessed_triples)
    preprocessed_example += " ."
    return preprocessed_example


def encode(sparql):
    """Encode sparql.

    sparql will not be a valid SPARQL query afterwards and has to be decoded by decode() to make it valid again.
    """
    s = sparql
    s = do_replacements(s, ENCODING_REPLACEMENTS)
    s = encode_datatype(s)
    # s = encode_uri_by_label(s)
    return s


def decode(encoded_sparql):
    """"Decode encoded sparql to make it a valid sparql query again."""
    s = encoded_sparql
    # s = decode_label_by_uri(s)
    s = decode_datatype(s)
    s = revert_replacements(s, ENCODING_REPLACEMENTS)
    return s


def decode_file(file):
    """Decode a file of encoded SPARQLs."""
    with open(file) as f:
        encoded_sparqls = [decode(line) for line in f]

    return encoded_sparqls


def uri_to_prefix(s):
    """Substitute the default SPARQL URIs with their prefixes.

    PREFIX_SUBSTITUTION defines the substitutions to be done. For one row, all column entries are substituted by the
    last column entry.

    Args:
        s: string where the substitution is made.
    """
    for row in PREFIX_SUBSTITUTION:
        encoding = row[-1]
        for original in row[:-1]:
            s = re.sub(f"<{original}([^>]*)>", f"{encoding}\\1", s)
    return s


def prefix_to_uri(s):
    """Substitute the default SPARQL URIs into their corresponding prefix.

    PREFIXES defines the substitutions to be done. The key is substituted by the value and chevrons are put around.

    Args:
        s: string where the substitution is made.
    """
    for prefix, substitute in PREFIXES.items():
        s = re.sub(f"\\b{prefix}(([^\\s.,;]|(\\.[^\\s,;]))+)", f"<{substitute}\\1>", s)
    return s


def sparql_keyword_to_lower_case(sparql):
    """Convert all SPARQL keywords in sparql to lower case."""
    normalize_s = []
    for token in sparql.split():
        beginning_subtoken = re.search(r"^\w+", token)
        if beginning_subtoken is not None:
            beginning_subtoken = beginning_subtoken.group()
            if beginning_subtoken.upper() in SPARQL_KEYWORDS:
                token = re.sub(r"^\w+", beginning_subtoken.lower(), token)
        normalize_s.append(token)
    sparql = " ".join(normalize_s)
    return sparql


def do_replacements(sparql, replacements, remove_successive_whitespaces=True):
    """Replace string occurrences in sparql by some replacement.

    For each row in replacements, replace each column entry by the second to last column entry.

    Args:
        sparql: some string.
        replacements: A list of lists.
        remove_successive_whitespaces: If true, remove successive whitespaces in ourput.
    """
    s = sparql
    for r in replacements:
        encoding = r[-2]
        for original in r[:-2]:
            s = s.replace(original, encoding)
    if remove_successive_whitespaces:
        s = re.sub(r" +", " ", s)
    return s


def revert_replacements(decoded_sparql, replacements, remove_successive_whitespaces=True):
    """Replace string occurrences in sparql by some replacement.

    For each row in replacements, replace the second to last column entry by the last column entry.

    Args:
        decoded_sparql: some string.
        replacements: A list of lists.
        remove_successive_whitespaces: If true, remove successive whitespaces in ourput.
    """
    s = decoded_sparql
    for r in replacements:
        encoding = r[-2]
        decoding = r[-1]
        s = s.replace(encoding, decoding)
    if remove_successive_whitespaces:
        s = re.sub(r" +", " ", s)
    return s


def encode_datatype(sparql):
    """Encode "^^" with " datatype "."""
    s = sparql
    s = s.replace("^^", " datatype ")
    return s


def decode_datatype(encoded_sparql):
    """Decode " datatype " to "^^" such that the SPARQL keyword "datatype" is not decoded.
    
    The SPARQL keyword DATATYPE can also be written in lowercase, so we have two kinds of datatype in our encoded 
    sparql.

    We assume all single quotes ' to be replaces by double quotes " beforehand."""
    s = encoded_sparql
    s = re.sub(r"(\") datatype ", r"\1^^", s)
    return s


def encode_uri_by_label(s):
    """Replace "<prefix:><path>" by "<prefix:> <label_of_the_corresponding_URI> :end_label".

    ":end_label" should be part of the tokenizer vocabulary.
    Excluded prefixes are: "xsd:".
    """
    excluded = ["xsd:"]
    prefixes = list(PREFIXES.keys())
    prefixes = [elem for elem in prefixes if elem not in excluded]
    for prefix in prefixes:
        s = re.sub(f"(\\b{prefix})(([^\\s.,;]|(\\.[^\\s,;]))+)", generate_label_encoding, s)
    s = re.sub(r" +", " ", s)
    return s


def test_label_encoding(sparql):
    encoded = encode_uri_by_label(sparql).strip()
    decoded = decode_label_by_uri(encoded).strip()
    lev = distance.levenshtein(sparql, decoded)
    if lev > 1:
        print(lev)
        print(sparql)
        print(decoded)
        print(encoded)
        print("")

    # assert decoded == sparql


def generate_label_encoding(match):
    """Generates the string for "<prefix:><path>"  which is "<prefix:> <label_of_the_corresponding_URI> :end_label".

    Only supports english labels, i.e. "<label>"@en.

    Args:
        match: A re.Match object.
    Returns:
        string: "<prefix:> <label_of_the_corresponding_URI> :end_label" if a label was found.
                "<prefix:><path>" else.
    """
    prefix = match.group(1)
    path = match.group(2)
    label = None

    uri = '<' + PREFIXES[prefix] + path + '>'
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

    Args:
        s: The string where labels should be decoded.

    Returns:
        A string with decoded labels if some were found.
    """
    prefixes = list(PREFIXES.keys())
    prefixes_regex = '|'.join(prefixes)
    s = re.sub(f"(\\b({prefixes_regex})((?!{prefixes_regex})|(.(?!{prefixes_regex}))*?):end_label)",
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
        whole_match = match.group(1)
        return whole_match
    prefix_uri = uri_to_prefix("<" + uri + ">")
    return prefix_uri


def decode_label_with_entity_linking(s: str, context: str) -> str:
    """Replace a label with a uri found by entity recognition on the label.

    Replace "<prefix:> <label_of_the_corresponding_URI> :end_label" by "<prefix:><path>".

    Args:
        s: The string where labels should be decoded.
        context: The string where entities are recognized and then linked to some uri. If a recognized entity is
                 the same as a label in s, it is replaced by the corresponding uri.

    Returns:
        A string with decoded labels if some were found.
    """
    response = query_dbspotlight(context, confidence=0.1)
    if "Resources" not in response:
        resources = list()
    else:
        resources = response["Resources"]
    text_to_uri = dict()
    for linked_entity in resources:
        if "@URI" in linked_entity and "@surfaceForm" in linked_entity:
            text_to_uri[linked_entity["@surfaceForm"]] = linked_entity["@URI"]
    prefixes = list(PREFIXES.keys())
    prefixes_regex = '|'.join(prefixes)
    for match in re.finditer(f"(\\b(({prefixes_regex})((?!{prefixes_regex})|(.(?!{prefixes_regex}))*?)):end_label)", s):
        whole_match = match.group(1)
        prefix_label = match.group(2).strip()
        label = match.group(4).strip()
        if label in text_to_uri:
            s = re.sub(whole_match, '<' + text_to_uri[label] + '>', s)
        elif prefix_label in text_to_uri:
            s = re.sub(whole_match, '<' + text_to_uri[prefix_label] + '>', s)
    s = uri_to_prefix(s)
    return s
