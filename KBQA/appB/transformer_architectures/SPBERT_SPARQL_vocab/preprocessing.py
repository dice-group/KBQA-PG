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

PREFIX_EQUIVALENTS = [
    ["onto:", "dbo:"],
    ["res:", "dbr:"],
]
SPARQL_KEYWORDS = {
    "PREFIX",
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
    ["<=", " less equal ", " <= "],
    [">=", " greater equal ", " >= "],
    ["!=", " not equal ", " != "],
    ["=", " equal ", " = "],
    ["< ", " less than ", " < "],
    [" >", " greater than ", " > "],
    ["||", " logical or ", " || "],
    ["&&", " logical and ", " && "],
    ["!", " logical not ", " ! "],
    ["@en", " language English ", "@en "],  # For now, we are only considering english literals.
    ["{", " bracket open", " { "],  # No space after " bracket open" to enable successive occurrences.
    ["}", " bracket close", " } "],
]
IRI_SCHEMES = ["http:",
               "https:",
               "ftp:",
               "mailto:",
               "file:",
               "data:",
               "irc:",
               "bif:",  # The "bif" prefix seems to also be recognized as schema from DBpedia (and Virtuoso in general).
               "sql:",  # See bif.
               "urn:yahoo:maps",  # See bif.
               ]
PREFIX_EXCEPTIONS = [["bif:", "bif:"],
                     ["sql:", "sql:"],
                     ["y:", "urn:yahoo:maps"]]


def load_prefixes() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Load the predefined DBpedia prefixes from prefixes/prefixes.txt or prefixes/prefixes.pickle if it exists.

    Returns: A tuple of three dicts.
        - The first element is a map from prefix to the corresponding uri.
        - The second a map from uri to prefix.
        - The third is equivalent to the second with the URIs changed to "https://" instead of "http://".
    """
    path = Path("prefixes/prefixes.txt")
    pickle_path = path.with_suffix(".pickle")
    if pickle_path.exists():
        with open(pickle_path, 'rb') as file:
            prefix_to_uri_, uri_to_prefix_, https_uri_to_prefix_ = pickle.load(file)
        return prefix_to_uri_, uri_to_prefix_, https_uri_to_prefix_
    if not path.exists():
        return dict(), dict(), dict()
    with open(path, 'r', encoding="utf-8") as file:
        prefix_to_uri_ = dict()
        uri_to_prefix_ = dict()
        https_uri_to_prefix_ = dict()
        for line in file:
            line = line.strip()
            prefix, uri = line.split()
            prefix += ':'
            https_uri = re.sub("^http", "https", uri)
            prefix_to_uri_[prefix] = uri
            uri_to_prefix_[uri] = prefix
            https_uri_to_prefix_[https_uri] = prefix
    with open(pickle_path, 'wb') as file:
        pickle.dump((prefix_to_uri_, uri_to_prefix_, https_uri_to_prefix_), file)
    return prefix_to_uri_, uri_to_prefix_, https_uri_to_prefix_


PREFIX_TO_URI, URI_TO_PREFIX, HTTPS_URI_TO_PREFIX = load_prefixes()


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
    with open(natural_language_file_path, "w", encoding="utf-8") as en_file, \
            open(triples_file_path, "w", encoding="utf-8") as triple_file, \
            open(sparql_file_path, "w", encoding="utf-8") as sparql_file, \
            open(input_file_path, "r", encoding="utf-8") as input_file:
        data_json = json.load(input_file)
        for element in data_json["questions"]:
            en_file.write(element["question"] + "\n")
            sparql_file.write(element["query"] + "\n")
            if len(element["triples"]) == 0:
                triple_file.write('\n')
            else:
                triple_file.write(
                    " . ".join(encode_new_line(element["triples"])) + " .\n")
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
        with open(output_file_checkpoint_state_path, "rb") as state_file:
            num_stored_examples = pickle.load(state_file)
    else:
        num_stored_examples = 0
    with open(input_file_path, "r", encoding="utf-8") as input_file, \
            open(output_file_checkpoint_data_path, "a", encoding="utf-8") as checkpoint_file:
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
    s = do_replacements(s, VALID_SPARQL_REPLACEMENTS)
    s = sparql_keyword_to_lower_case(s)
    s = re.sub(r"@en", r"@en", s, flags=re.IGNORECASE)  # English language tag to lower case.
    # bif:contains can be used as whole IRI or prefixed IRI. Normalize to prefix.
    s = re.sub(r"<bif:contains>", "bif:contains", s)
    s = inline_and_remove_base(s)
    s = inline_and_remove_prefixes(s)
    s = remove_zero_timezone(s)
    s = uri_to_prefix(s)
    s = normalize_prefixes(s)
    return s


def remove_zero_timezone(s: str) -> str:
    """Remove timezones with T00:00:00Z time.

    Args:
        s: String where the removal is done.

    Returns:
        String with removed zero-timezone.
    """
    s = re.sub(r"(\d{4}-\d{2}-\d{2})T00:00:00Z", r"\1", s)
    return s


def inline_and_remove_base(s: str) -> str:
    """Inline the BASE IRI of the SPARQL s and remove it.

    If the IRI of a "<IRI>" occurrence does not start with any scheme in IRI_SCHEME, the BASE-IRI is added as prefix if
    it exists.

    Args:
        s: SPARQL string.
    Returns:
        String with inlined and removed BASE.
    """
    match = re.match(r"\s*BASE\s*<([^>]*)>", s, flags=re.IGNORECASE)
    if match is not None:
        base_iri = match.group(1)
        s = re.sub(r"\s*BASE\s*<([^>]*)>", "", s, flags=re.IGNORECASE)  # Remove BASE.
        s = s.lstrip()
        schemes_regex = '|'.join(IRI_SCHEMES)
        s = re.sub(f"<(?!({schemes_regex}))([^>]*)>", f"<{base_iri}\\2>", s)
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
    # We store all found prefixes in a map to keep the last found URL for some prefix only and replace it afterwards.
    prefix_url_dict = dict()
    for pre_name, pre_url in re.findall(r"PREFIX\s*([^:]*):\s*<([^>]*)>", s, flags=re.IGNORECASE):
        s = re.sub(f"PREFIX\\s*{pre_name}:\\s*<{pre_url}>", "", s, flags=re.IGNORECASE)  # Remove prefix.
        s = s.lstrip()
        prefix_url_dict[pre_name] = pre_url
    for pre_name, pre_url in prefix_url_dict.items():
        if pre_name == "":
            empty_prefix_name = True
            empty_prefix_uri = pre_url
        else:
            # Inline prefix.
            s = re.sub(f"(?!(<))\\b{pre_name}:([^\\s.,;]*)", f"<{pre_url}\\2>", s)
    if empty_prefix_name:
        # Empty prefix ':<something>' is replaced by its URI if it is preceded by a whitespace or a SPARQL term
        # delimiter ('.', ',', ';').
        s = re.sub(f"([.,;\\s]):([^\\s.,;]*)", f"\\1<{empty_prefix_uri}\\2>", s)
    return s


def normalize_prefixes(s: str) -> str:
    """Replace some prefixes with equivalent ones defined in PREFIX_EQUIVALENTS.

    All entries in one row are replaced by the last row element.

    Args:
        s: The string where the replacing is done

    Returns:
        The string with replacements.
    """
    for row in PREFIX_EQUIVALENTS:
        encoding = row[-1]
        for elem in row[:-1]:
            s = re.sub(elem, encoding, s)
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


def upper_bound_literal(triples_example: str, max_literal_length: int = 60) -> str:
    """If a literal exceeds the max_literal_length, it is truncated at this length.

    Args:
        triples_example: The triples where literals are truncated.
        max_literal_length: The number of chars at which literals are truncated. Defaults to 60 which are six long
                            words.

    Returns:
        String with truncated literals.
    """
    def truncate_match(match: re.Match) -> str:
        """Function to be called on each occurrence of a literal.

        Args:
            match: The Match found by re.sub.

        Returns:
            The replacement string.
        """
        if match.group(1) is not None:
            literal = match.group(1)
            quotation = '"""'
        elif match.group(3) is not None:
            literal = match.group(3)
            quotation = "'''"
        elif match.group(5) is not None:
            literal = match.group(5)
            quotation = '"'
        else:  # match.group(6) is not None.
            literal = match.group(6)
            quotation = "'"
        if len(literal) > max_literal_length:
            return quotation + literal[:max_literal_length] + quotation
        whole_match = match.group(0)
        return whole_match
    s = triples_example
    s = re.sub(r"\"\"\"((?!\"\"\")|(.(?!\"\"\"))*?.)\"\"\"|"
               r"\'\'\'((?!\'\'\')|(.(?!\'\'\'))*?.)\'\'\'|"
               r"\"([^\"]*)\"|"
               r"\'([^\']*)\'", truncate_match, s)
    return s


def encode(sparql):
    """Encode sparql.

    sparql will not be a valid SPARQL query afterwards and has to be decoded by decode() to make it valid again.
    """
    s = sparql
    s = do_replacements(s, ENCODING_REPLACEMENTS)
    s = encode_asterisk(s)
    s = encode_datatype(s)
    # s = encode_uri_by_label(s)
    return s


def decode(encoded_sparql):
    """"Decode encoded sparql to make it a valid sparql query again."""
    s = encoded_sparql
    # s = decode_label_by_uri(s)
    s = decode_datatype(s)
    s = decode_asterisk(s)
    s = revert_replacements(s, ENCODING_REPLACEMENTS)
    return s


def decode_file(file):
    """Decode a file of encoded SPARQLs."""
    with open(file) as f:
        encoded_sparqls = [decode(line) for line in f]

    return encoded_sparqls


def uri_to_prefix(s):
    """Substitute the default SPARQL URIs and the "https://" versions with their prefixes.

    PREFIX_TO_URI defines the substitutions to be done. Each URI with a prefix "http://" is also considered with the
    prefix "https://".

    Args:
        s: string where the substitution is made.

    Returns:
        The string with substituted URIs.

    Note: If we find a substitution for some URI prefix but the remainder still includes a '/', we do not substitute
          because this is wrong in many cases. SPARQL still allows it.
    """
    for prefix, uri in PREFIX_TO_URI.items():
        s = re.sub(f"<{uri}([^/>\"{{}}|^`\\\\]*)>", f"{prefix}\\1", s)

    for https_uri, prefix in HTTPS_URI_TO_PREFIX.items():
        s = re.sub(f"<{https_uri}([^/>\"{{}}|^`\\\\]*)>", f"{prefix}\\1", s)
    return s


def prefix_to_uri(s):
    """Substitute the default SPARQL URIs into their corresponding prefix.

    PREFIX_TO_URI defines the substitutions to be done. The key is substituted by the value and chevrons are put around.

    Args:
        s: string where the substitution is made.

    Returns:
        The string with prefixes substituted by URIs.

    Note: We do not substitute prefixes if they follow a '<' because these could be schemas e.g. "bif:".
    """
    for prefix, substitute in PREFIX_TO_URI.items():
        s = re.sub(f"(?!(<))\\b{prefix}(([^\\s.,;]|(\\.[^\\s,;]))*)", f"<{substitute}\\2>", s)
    return s


def sparql_keyword_to_lower_case(s):
    """Convert all SPARQL keywords from SPARQL_KEYWORDS in s to lower case.

    Args:
        s: The string where keywords are converted.

    Returns:
        The string with converted keywords.
    """
    keyword_regex = '|'.join(SPARQL_KEYWORDS)
    s = re.sub(f"\\s*\\b({keyword_regex})\\b\\s*", r" \1 ", s)  # Put one space around each found upper case keyword.
    
    normalize_s = []
    for token in s.split():
        beginning_subtoken = re.search(r"^\w+", token)
        if beginning_subtoken is not None:
            beginning_subtoken = beginning_subtoken.group()
            if beginning_subtoken.upper() in SPARQL_KEYWORDS:
                token = re.sub(r"^\w+", beginning_subtoken.lower(), token)
        normalize_s.append(token)
    s = " ".join(normalize_s)
    return s


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


def encode_asterisk(s: str) -> str:
    """Replaces '*' by " all variables " when it is used for selecting all variables.

    Args:
        s: The string where the replacement is done.

    Returns:
        The string with replacements.
    """
    s = re.sub(r"((SELECT\s*(DISTINCT|REDUCED)?)|DESCRIBE)\s*\*", r"\1 all variables ", s, flags=re.IGNORECASE)
    s = re.sub(r" +", " ", s)
    return s


def decode_asterisk(s: str) -> str:
    """Replaces " all variables " by ' * ' when it is used for selecting all variables.

    Args:
        s: The string where the replacement is done.

    Returns:
        The string with replacements.
    """
    s = re.sub(r"((SELECT\s*(DISTINCT|REDUCED)?)|DESCRIBE)\s*all variables", r"\1 * ", s, flags=re.IGNORECASE)
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

    Args:
        encoded_sparql: The string where datatypes should be decoded.
    Returns:
        The decoded string.
    """
    s = encoded_sparql
    s = re.sub(r"(\"\"\"|\'\'\'|\"|\') datatype ", r"\1^^", s)
    return s


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
