"""Utility lists, dicts and functions for preprocessing data."""
import functools
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
    [" !", " logical not ", " ! "],
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


def load_prefixes() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Load the predefined DBpedia prefixes from prefixes/prefixes.txt or prefixes/prefixes.pickle if it exists.

    Returns: A tuple of three dicts.
        - The first element is a map from prefix to the corresponding uri.
        - The second a map from uri to prefix.
        - The third is equivalent to the second with the URIs changed to "https://" instead of "http://".
    """
    pwd = Path(os.path.dirname(__file__))
    path = pwd / "prefixes/prefixes.txt"
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


def preprocess_qtq_file_base(input_file_path: Union[str, os.PathLike, Path],
                             output_folder_path: Union[str, os.PathLike, Path] = Path("preprocessed_data_files"),
                             keep_separated_input_file: bool = False,
                             separated_input_files_folder_path: Union[str, os.PathLike, Path] =
                             Path("separated_data_files"),
                             checkpointing_period: int = 10,
                             *,
                             encoder: Callable[[str], str]) -> tuple[Path, Path, Path]:
    """Separate and preprocess a JSON qtq-file into three files, question-, triple-, sparql-file.

    Let file_name_without_json be the file_name without the trailing ".json".
    Store the preprocessed questions in <output_folder_path>/<file_name_without_json>.en.
    Store the preprocessed triples in <output_folder_path>/<file_name without_json>.triple.
    Store the preprocessed SPARQL queries in <output_folder_path>/<file_name_without_json>.sparql.

    Also replaces '\n' by ',' on the triples of the qtq-file.

    Args:
        input_file_path: The qtq-file-path. Must be a valid JSON with suffix ".json".
        output_folder_path: The folder-path where the preprocessed files are stored. Defaults to
                            "preprocessed_data_files".
        keep_separated_input_file: If True, store the separated qtq-file in separated_input_files_folder_path.
        separated_input_files_folder_path: The input-file is separated into questions, triples and SPARQLs before
                                           preprocessing. This is folder-path where these intermediate files are stored.
                                           Defaults to "separated_data_files".
        checkpointing_period: For every checkpointing_period of processed examples, the examples are stored in
                              <output_file_path>.checkpoint_data and the algorithm state in
                              <checkpoint_data>.checkpoint_state. If the algorithm is interrupted, it can be resumed
                              from the checkpoint by calling it with the same arguments.
        encoder: The encoding function.

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
    preprocessed_triples_file_path = preprocess_triples_file_base(input_file_path=triples_file_path,
                                                                  output_file_path=preprocessed_triples_file_path,
                                                                  checkpointing_period=checkpointing_period,
                                                                  encoder=encoder)
    preprocessed_sparql_file_path = preprocess_sparql_file_base(input_file_path=sparql_file_path,
                                                                output_file_path=preprocessed_sparql_file_path,
                                                                checkpointing_period=checkpointing_period,
                                                                encoder=encoder)
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

    Also replaces '\n' by ',' on the triples of the qtq-file.

    Args:
        input_file_path: The path to the input file. Suffix must be ".json".
        output_folder_path: The path where the separated qtq-file parts should be stored. Defaults to
                            "separated_data_files".

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
                    " . ".join(replace_new_line_char_by_comma(element["triples"])) + " .\n")
    return natural_language_file_path, triples_file_path, sparql_file_path


def replace_new_line_char_by_comma(triples: list) -> list:
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


def preprocess_sparql_file_base(input_file_path: Union[str, os.PathLike, Path],
                                output_file_path: Union[str, os.PathLike, Path, None] = None,
                                checkpointing_period: int = 10,
                                *,
                                encoder: Callable[[str], str]) -> Path:
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
        encoder: The encoding function.

    Returns:
        The path of the preprocessed file.
    """
    preprocess_sparql = functools.partial(preprocess_sparql_base, encoder=encoder)
    output_file_path = preprocess_file(preprocessing_function=preprocess_sparql, input_file_path=input_file_path,
                                       output_file_path=output_file_path, checkpointing_period=checkpointing_period,
                                       progress_bar_description="Amount of preprocessed SPARQLs",
                                       progress_bar_unit="SPARQL")
    return output_file_path


def preprocess_sparql_base(s: str, *, encoder: Callable[[str], str]) -> str:
    """Preprocess a SPARQL string.

    Args:
        s: The string to be preprocessed.
        encoder: The encoding function.

    Returns:
        The preprocessed string.
    """
    s = do_valid_preprocessing(s)
    s = encoder(s)
    s = s.strip()
    s = re.sub(r" +", " ", s)
    return s


def preprocess_triples_file_base(input_file_path: Union[str, os.PathLike, Path],
                                 output_file_path: Union[str, os.PathLike, Path, None] = None,
                                 checkpointing_period: int = 10,
                                 *,
                                 encoder: Callable[[str], str]) -> Path:
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
        encoder: The encoding function.

    Returns:
        The path of the preprocessed file.
    """
    preprocess_triples = functools.partial(preprocess_triples_base, encoder=encoder)
    output_file_path = preprocess_file(preprocessing_function=preprocess_triples, input_file_path=input_file_path,
                                       output_file_path=output_file_path, checkpointing_period=checkpointing_period,
                                       progress_bar_description="Amount of preprocessed triple-sets",
                                       progress_bar_unit="triple-set")
    return output_file_path


def preprocess_triples_base(triples_example: str, *, encoder: Callable[[str], str]) -> str:
    """Preprocess a string of triples.

    The string should not contain new line characters.

    Args:
        triples_example: The string of triples to be preprocessed.
        encoder: The encoding function.

    Returns:
        The preprocessed triples string.
    """
    s = triples_example
    s = upper_bound_literal(s)  # Max six long words.
    s = preprocess_sparql_base(s, encoder=encoder)
    return s


def do_valid_preprocessing(sparql: str) -> str:
    """Preprocessing part which keeps the SPARQL sparql a valid SPARQL.

    Args:
        sparql: String which the preprocessing is done on.

    Returns:
        Preprocessed SPARQL with the same semantic as sparql.
    """
    s = sparql
    s = do_replacements(s, VALID_SPARQL_REPLACEMENTS)
    s = sparql_keyword_to_lower_case(s)
    s = re.sub(r"@en", r"@en", s, flags=re.IGNORECASE)  # English language tag to lower case.
    # bif:contains can be used as whole IRI or prefixed IRI. Normalize to prefix.
    s = re.sub(r"<bif:contains>", "bif:contains", s)
    s = inline_and_remove_base(s)
    s = inline_and_remove_prefixes(s)
    s = uri_to_prefix(s)
    s = normalize_prefixes(s)
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


def uri_to_prefix(s):
    """Substitute the default SPARQL URIs and the "https://" versions with their prefixes.

    PREFIX_TO_URI defines the substitutions to be done. Each URI with a prefix "http://" is also considered with the
    prefix "https://".

    Args:
        s: string where the substitution is made.

    Returns:
        The string with substituted URIs.

    Note: DBpedia does not allow prefixes to be used while the remainder of the URI still carries a '/'. SPARQL allows
          it and we benefit also from allowing it.
    """
    for prefix, uri in PREFIX_TO_URI.items():
        s = re.sub(f"<{uri}([^>]*)>", f"{prefix}\\1", s)

    for https_uri, prefix in HTTPS_URI_TO_PREFIX.items():
        s = re.sub(f"<{https_uri}([^>]*)>", f"{prefix}\\1", s)
    return s


def prefix_to_uri(s):
    """Substitute default DBpedia prefixes by their URI.

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


def decode_file_base(input_file_path: Union[str, os.PathLike, Path],
                     output_file_path: Union[str, os.PathLike, Path, None] = None,
                     checkpointing_period: int = 10,
                     *,
                     decoder: Callable[[str], str]) -> Path:
    """Decode a file of encoded SPARQLs.

    Args:
        input_file_path: The path to the file of encoded SPARQLs.
        output_file_path: The path of the decoded SPARQLs. The file is created if it does not exist or
                          overwritten if it already exists. If None, defaults to
                          "decoded_files/<input_file_name>" where <input_file_name> is the name of the
                          input-file.
        checkpointing_period: For every checkpointing_period of decoded examples, the examples are stored in
                              <output_file_path>.checkpoint_data and the algorithm state in
                              <checkpoint_data>.checkpoint_state. If the algorithm is interrupted, it can be resumed
                              from the checkpoint by calling it with the same arguments.
        decoder: The decoding function.

    Returns:
        The path of the decoded file.
    """
    input_file_path = Path(input_file_path)
    if output_file_path is None:
        output_file_path = Path("decoded_files") / input_file_path.name
    else:
        output_file_path = Path(output_file_path)
    output_file_path = preprocess_file(preprocessing_function=decoder, input_file_path=input_file_path,
                                       output_file_path=output_file_path, checkpointing_period=checkpointing_period,
                                       progress_bar_description="Amount of decoded SPARQLs",
                                       progress_bar_unit="SPARQL")
    return output_file_path


def sparql_encoder_levenshtein_dist_on_file_base(input_file_path: Union[str, os.PathLike, Path],
                                                 log_lower_bound: float = math.inf,
                                                 *,
                                                 encoder: Callable[[str], str],
                                                 decoder: Callable[[str], str]) -> float:
    """Preprocess the given data and then calculate the Levenshtein distance between encoding and decoding it.

    The SPARQL preprocessing part is applied for preprocessing.

    Args:
        input_file_path: A path-like object to the file with the SPARQLs.
        log_lower_bound: Print logging information to stdout for each example which has an equal or higher Levenshtein
                         distance than log_lower_bound.
        encoder: The encoding function.
        decoder: The decoding function.

    Returns:
        The mean Levenshtein distance.
    """
    input_file_path = Path(input_file_path)
    cumulative_dist = 0
    amount = 0
    with open(input_file_path, "r", encoding="utf-8") as file:
        for sparql in tqdm(file, desc="Amount of scored SPARQLs", unit="SPARQL"):
            dist = sparql_encoder_levenshtein_dist_base(sparql.strip(),
                                                        log_lower_bound=log_lower_bound,
                                                        encoder=encoder,
                                                        decoder=decoder)
            cumulative_dist += dist
            amount += 1
    mean_dist = cumulative_dist / amount
    return mean_dist


def sparql_encoder_levenshtein_dist_base(sparql: str,
                                         log_lower_bound: float = math.inf,
                                         *,
                                         encoder: Callable[[str], str],
                                         decoder: Callable[[str], str]) -> float:
    """Preprocess sparql and then calculate the Levenshtein distance between encoding and decoding it.

    The SPARQL preprocessing part is applied for preprocessing.

    Args:
        sparql: A SPARQL string.
        log_lower_bound: Print logging information to stdout for each example which has an equal or higher Levenshtein
                         distance than log_lower_bound.
        encoder: The encoding function.
        decoder: The decoding function.

    Returns:
        The Levenshtein distance.
    """
    preprocessed = do_valid_preprocessing(sparql)
    preprocessed_normalized = uri_to_prefix(preprocessed)
    preprocessed_normalized = normalize_prefixes(preprocessed_normalized)
    preprocessed_normalized = prefix_to_uri(preprocessed_normalized)
    encoded = encoder(preprocessed)
    decoded = decoder(encoded)
    dist = distance.levenshtein(preprocessed_normalized, decoded)
    if dist >= log_lower_bound:
        print("\n--------------------------------------------------")
        print(f"SPARQL:\n{sparql}")
        print(f"\nPreprocessed:\n{preprocessed}")
        print(f"\nPreprocessed Normalized:\n{preprocessed_normalized}")
        print(f"\nEncoded:\n{encoded}")
        print(f"\nDecoded:\n{decoded}")
        print(f"\nDifference:\n")
        diff = ndiff(preprocessed_normalized.split(), decoded.split())
        print('\n'.join(diff))
        print(f"\nDistance: {dist}")
        print("----------------------------------------------------")
    return dist


def test_do_valid_preprocessing_on_file(input_file_path: Union[str, os.PathLike, Path]) -> tuple[float, int]:
    """Test the function do_valid_preprocessing on SPARQLs in input_file_path.

    Args:
        input_file_path: A path-like object to the file with the SPARQLs.

    Returns: Tuple of 2 elements:
        - The ratio of valid preprocessed SPARQLs to all SPARQLs which were valid before preprocessing.
        - The number of not valid unprocessed SPARQLs.
    """
    input_file_path = Path(input_file_path)
    num_not_valid = 0
    num_unprocessed_not_valid = 0
    num_valid = 0
    with open(input_file_path, "r", encoding="utf-8") as file:
        for sparql in tqdm(file, desc="Amount of tested SPARQLs", unit="SPARQL"):
            ret = test_do_valid_preprocessing(sparql)
            if ret == 1:
                num_valid += 1
            elif ret == 0:
                num_not_valid += 1
            elif ret == -1:
                num_unprocessed_not_valid += 1
    ratio = num_valid / (num_valid + num_not_valid)
    print(f"Number of valid preprocessed SPARQLs: {num_valid}")
    print(f"Number of not valid preprocessed SPARQLs: {num_not_valid}")
    print(f"Number of not valid SPARQLs before preprocessing: {num_unprocessed_not_valid}")
    print(f"Ratio between valid and all SPARQLs which were valid before preprocessing: {ratio}")
    return ratio, num_unprocessed_not_valid


def test_do_valid_preprocessing(sparql: str) -> int:
    """Test the function do_valid_preprocessing on SPARQL sparql.

    Args:
        sparql: SPARQL on which the preprocessing is done in.

    Returns:
        1, if the preprocessing is valid. 0, if it is not valid. -1, if the unprocessed SPARQL is not valid.
    """
    preprocessed_sparql = do_valid_preprocessing(sparql)

    # Query SPARQL
    SPARQL_WRAPPER.setQuery(sparql)
    try:
        answer = SPARQL_WRAPPER.queryAndConvert()
    except BaseException as excepion:
        print("\n--------------------------------------------------")
        print(f"An exception occurred at unprocessed SPARQL:\n{sparql}")
        print(f"Exception:\n{excepion}")
        print("----------------------------------------------------")
        return -1

    # Query Preprocessed SPARQL
    SPARQL_WRAPPER.setQuery(preprocessed_sparql)
    try:
        answer = SPARQL_WRAPPER.queryAndConvert()
    except BaseException as excepion:
        print("\n--------------------------------------------------")
        print(f"An exception occurred at preprocessed SPARQL:\n{preprocessed_sparql}")
        print(f"Exception:\n{excepion}")
        print(f"The corresponding unprocessed SPARQL is:\n{sparql}")
        print("----------------------------------------------------")
        return 0
    return 1
