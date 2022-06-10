r"""Utility lists, dicts and functions for preprocessing data."""
from difflib import ndiff
import functools
import json
import math
import os
from pathlib import Path
import pickle
import random
import re
from typing import Callable
from typing import Union

import distance
import numpy as np
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper
from tqdm import tqdm

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
    ["rdf:type", "a", "a"],
    ["$", "?", "?"],  # Normalize to one variable symbol
    ["{", " { ", " { "],
    ["}", " } ", " } "],
]
ENCODING_REPLACEMENTS = [
    ["?", " variable: ", " ?"],
    ["<=", " less equal ", " <= "],
    [">=", " greater equal ", " >= "],
    ["!=", " not equal ", " != "],
    ["=", " equal ", " = "],
    ["< ", " less than ", " < "],
    [" >", " greater than ", " > "],
    ["||", " logical or ", " || "],
    ["&&", " logical and ", " && "],
    [" !", " logical not ", " ! "],
    [
        "@en",
        " language English ",
        "@en ",
    ],  # For now, we are only considering english literals.
    [
        "{",
        " bracket open",
        " { ",
    ],  # No space after " bracket open" to enable successive occurrences.
    ["}", " bracket close", " } "],
]
IRI_SCHEMES = [
    "http:",
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
    r"""Load the predefined DBpedia prefixes from prefixes/prefixes.txt or prefixes/prefixes.pickle if it exists.

    Returns
    -------
    A tuple of three dicts:
        - The first element is a map from prefix to the corresponding uri.
        - The second a map from uri to prefix.
        - The third is equivalent to the second with the URIs changed to "https://" instead of "http://".
    """
    pwd = Path(os.path.dirname(__file__))
    path = pwd / "prefixes/prefixes.txt"
    pickle_path = path.with_suffix(".pickle")
    if pickle_path.exists():
        with open(pickle_path, "rb") as file:
            prefix_to_uri_, uri_to_prefix_, https_uri_to_prefix_ = pickle.load(file)
        return prefix_to_uri_, uri_to_prefix_, https_uri_to_prefix_
    if not path.exists():
        return dict(), dict(), dict()
    with open(path, "r", encoding="utf-8") as file:
        prefix_to_uri_ = dict()
        uri_to_prefix_ = dict()
        https_uri_to_prefix_ = dict()
        for line in file:
            line = line.strip()
            prefix, uri = line.split()
            prefix += ":"
            https_uri = re.sub("^http", "https", uri)
            prefix_to_uri_[prefix] = uri
            uri_to_prefix_[uri] = prefix
            https_uri_to_prefix_[https_uri] = prefix
    with open(pickle_path, "wb") as file:
        pickle.dump((prefix_to_uri_, uri_to_prefix_, https_uri_to_prefix_), file)
    return prefix_to_uri_, uri_to_prefix_, https_uri_to_prefix_


PREFIX_TO_URI, URI_TO_PREFIX, HTTPS_URI_TO_PREFIX = load_prefixes()


def preprocess_qtq_file_base(
    input_file_path: Union[str, os.PathLike, Path],
    output_folder_path: Union[str, os.PathLike, Path] = Path("preprocessed_data_files"),
    keep_separated_input_file: bool = False,
    separated_input_files_folder_path: Union[str, os.PathLike, Path] = Path(
        "separated_data_files"
    ),
    checkpointing_period: int = 10,
    *,
    encoder: Callable[[str], str],
) -> tuple[Path, Path, Path]:
    r"""Separate and preprocess a JSON qtq-file into three files, question-, triple-, sparql-file.

    Let file_name_without_json be the file_name without the trailing ".json".
    Store the preprocessed questions in <output_folder_path>/<file_name_without_json>.en.
    Store the preprocessed triples in <output_folder_path>/<file_name without_json>.triple.
    Store the preprocessed SPARQL queries in <output_folder_path>/<file_name_without_json>.sparql.

    Also replaces '\n' by ',' on the triples of the qtq-file.

    Parameters
    ----------
    input_file_path : str, os.PathLike or Path
        The qtq-file-path. Must be a valid JSON with suffix ".json".
    output_folder_path : str, os.PathLike or Path, optional
        The folder-path where the preprocessed files are stored. Defaults to "preprocessed_data_files".
    keep_separated_input_file : bool, optional
        If True, store the separated qtq-file in separated_input_files_folder_path. Defaults to False.
    separated_input_files_folder_path : str, os.PathLike or Path, optional
        The input-file is separated into questions, triples and SPARQLs before preprocessing. This is folder-path where
        these intermediate files are stored. Defaults to "separated_data_files".
    checkpointing_period : int, optional
        For every checkpointing_period of processed examples, the examples are stored in
        <output_file_path>.checkpoint_data and the algorithm state in <checkpoint_data>.checkpoint_state. If the
        algorithm is interrupted, it can be resumed from the checkpoint by calling it with the same arguments. Defaults
        to 10.
    encoder : Callable[[str], str]
        The encoding function.

    Returns
    -------
    tuple of Path, Path, Path with elements:
        - Path to preprocessed natural language file.
        - Path to preprocessed triples file.
        - Path to preprocessed SPARQL file.

    Note
    ----
    Checkpointing is not applied on the data-separation step.
    """
    input_file_path = Path(input_file_path)
    output_folder_path = Path(output_folder_path)
    separated_input_files_folder_path = Path(separated_input_files_folder_path)
    if input_file_path.suffix != ".json":
        raise ValueError('input_file_path should be ending with ".json"')
    output_folder_path.mkdir(parents=True, exist_ok=True)
    natural_language_file_path, triples_file_path, sparql_file_path = separate_qtq_file(
        input_file_path=input_file_path,
        output_folder_path=separated_input_files_folder_path,
    )
    preprocessed_natural_language_file_path = (
        output_folder_path / input_file_path.with_suffix(".en").name
    )
    preprocessed_triples_file_path = (
        output_folder_path / input_file_path.with_suffix(".triple").name
    )
    preprocessed_sparql_file_path = (
        output_folder_path / input_file_path.with_suffix(".sparql").name
    )
    preprocessed_natural_language_file_path = preprocess_natural_language_file(
        input_file_path=natural_language_file_path,
        output_file_path=preprocessed_natural_language_file_path,
        checkpointing_period=checkpointing_period,
    )
    preprocessed_triples_file_path = preprocess_triples_file_base(
        input_file_path=triples_file_path,
        output_file_path=preprocessed_triples_file_path,
        checkpointing_period=checkpointing_period,
        encoder=encoder,
    )
    preprocessed_sparql_file_path = preprocess_sparql_file_base(
        input_file_path=sparql_file_path,
        output_file_path=preprocessed_sparql_file_path,
        checkpointing_period=checkpointing_period,
        encoder=encoder,
    )
    if not keep_separated_input_file:
        natural_language_file_path.unlink()
        triples_file_path.unlink()
        sparql_file_path.unlink()
        if not any(separated_input_files_folder_path.iterdir()):
            separated_input_files_folder_path.rmdir()
    return (
        preprocessed_natural_language_file_path,
        preprocessed_triples_file_path,
        preprocessed_sparql_file_path,
    )


def separate_qtq_file(
    input_file_path: Union[str, os.PathLike, Path],
    output_folder_path: Union[str, os.PathLike, Path] = "separated_data_files",
) -> tuple[Path, Path, Path]:
    r"""Separate a JSON qtq-file into three files, question-, triple-, sparql-file.

    Let file_name_without_json be the file_name without the trailing ".json".
    Store the questions in <output_folder_path>/<file_name_without_json>.en.
    Store the triples in <output_folder_path>/<file_name without_json>.triple.
    Store the SPARQL queries in <output_folder_path>/<file_name_without_json>.sparql.

    Also replaces '\n' by ',' on the triples of the qtq-file.

    Parameters
    ----------
    input_file_path : str, os.PathLike or Path
        The path to the input file. Suffix must be ".json".
    output_folder_path: str, os.PathLike or Path, optional
        The path where the separated qtq-file parts should be stored. Defaults to "separated_data_files".

    Returns
    -------
    tuple of Path, Path, Path with elements:
        - Path to preprocessed natural language file.
        - Path to preprocessed triples file.
        - Path to preprocessed SPARQL file.
    """
    input_file_path = Path(input_file_path)
    output_folder_path = Path(output_folder_path)
    if input_file_path.suffix != ".json":
        raise ValueError('input_file_path should be ending with ".json"')
    output_folder_path.mkdir(parents=True, exist_ok=True)
    natural_language_file_path = (
        output_folder_path / input_file_path.with_suffix(".en").name
    )
    triples_file_path = output_folder_path / input_file_path.with_suffix(".triple").name
    sparql_file_path = output_folder_path / input_file_path.with_suffix(".sparql").name
    with open(natural_language_file_path, "w", encoding="utf-8") as en_file, open(
        triples_file_path, "w", encoding="utf-8"
    ) as triple_file, open(
        sparql_file_path, "w", encoding="utf-8"
    ) as sparql_file, open(
        input_file_path, "r", encoding="utf-8"
    ) as input_file:
        data_json = json.load(input_file)
        for element in data_json["questions"]:
            en_file.write(element["question"] + "\n")
            sparql_file.write(element["query"] + "\n")
            if len(element["triples"]) == 0:
                triple_file.write("\n")
            else:
                triple_file.write(
                    " . ".join(replace_new_line_char_by_comma(element["triples"]))
                    + " .\n"
                )
    return natural_language_file_path, triples_file_path, sparql_file_path


def replace_new_line_char_by_comma(triples: list[str]) -> list[str]:
    r"""If a triple in triples has a '\n' character, replace it by ", ".

    Parameters
    ----------
    triples : list of str
        List of triples.

    Returns
    -------
    list of str
        List of encoded triples.
    """
    return [triple.replace("\n", ", ") for triple in triples]


def preprocess_file(
    preprocessing_function: Callable[[str], str],
    input_file_path: Union[str, os.PathLike, Path],
    output_file_path: Union[str, os.PathLike, Path, None] = None,
    checkpointing_period: int = 10,
    progress_bar_description: Union[str, None] = None,
    progress_bar_unit: str = "iteration",
) -> Path:
    r"""Preprocess a file with preprocessing_function.

    Parameters
    ----------
    preprocessing_function : Callable[[str], str]
        This functions is applied to each line in the input-file at input_file_path. The result is the respective line
        in the output-file at output_file_path.
    input_file_path : str, os.PathLike or Path
        The path of the file to preprocess.
    output_file_path : str, os.PathLike or Path, optional
        The path of the final preprocessed file. The file is created if it does not exist or overwritten if it already
        exists. If None, defaults to "preprocessed_data_files/<input_file_name>" where <input_file_name> is the name of
        the input-file.
    checkpointing_period : int, optional
        For every checkpointing_period of processed examples, the examples are stored in
        <output_file_path>.checkpoint_data and the algorithm state in <checkpoint_data>.checkpoint_state. If the
        algorithm is interrupted, it can be resumed from the checkpoint by calling it with the same arguments. Defaults
        to 10.
    progress_bar_description : str or None, optional
        A str which is shown in front of the progress bar. Defaults to None which disables the description.
    progress_bar_unit : str, optional
        A str which is the unit of the progress bar. Defaults to "iteration".

    Returns
    -------
    Path
        The path of the preprocessed file.
    """
    input_file_path = Path(input_file_path)
    if output_file_path is None:
        output_file_path = Path("preprocessed_data_files") / input_file_path.name
    else:
        output_file_path = Path(output_file_path)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_file_checkpoint_data_path = output_file_path.parent / (
        output_file_path.name + ".checkpoint_data"
    )
    output_file_checkpoint_state_path = output_file_path.parent / (
        output_file_path.name + ".checkpoint_state"
    )
    if output_file_checkpoint_state_path.exists():
        with open(output_file_checkpoint_state_path, "rb") as state_file:
            num_stored_examples = pickle.load(state_file)
    else:
        num_stored_examples = 0
    with open(input_file_path, "r", encoding="utf-8") as input_file, open(
        output_file_checkpoint_data_path, "a", encoding="utf-8"
    ) as checkpoint_file:
        for _ in range(num_stored_examples):
            input_file.readline()
        if num_stored_examples == 0:
            preprocessed_examples = ""
        else:
            preprocessed_examples = "\n"
        num_preprocessed_examples = 0
        for example in tqdm(
            input_file,
            desc=progress_bar_description,
            unit=progress_bar_unit,
            initial=num_stored_examples,
        ):
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


def preprocess_natural_language_file(
    input_file_path: Union[str, os.PathLike, Path],
    output_file_path: Union[str, os.PathLike, Path, None] = None,
    checkpointing_period: int = 10,
) -> Path:
    r"""Preprocess a natural language file.

    Parameters
    ----------
    input_file_path : str, os.PathLike or Path
        The path of the file to preprocess.
    output_file_path : str, os.PathLike or Path, optional
        The path of the final preprocessed file. The file is created if it does not exist or overwritten if it already
        exists. If None, defaults to "preprocessed_data_files/<input_file_name>" where <input_file_name> is the name of
        the input-file.
    checkpointing_period : int, optional
        For every checkpointing_period of processed examples, the examples are stored in
        <output_file_path>.checkpoint_data and the algorithm state in <checkpoint_data>.checkpoint_state. If the
        algorithm is interrupted, it can be resumed from the checkpoint by calling it with the same arguments. Defaults
        to 10.

    Returns
    -------
    Path
        The path of the preprocessed file.
    """
    output_file_path = preprocess_file(
        preprocessing_function=preprocess_natural_language_sentence,
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        checkpointing_period=checkpointing_period,
        progress_bar_description="Amount of preprocessed questions",
        progress_bar_unit="question",
    )
    return output_file_path


def preprocess_natural_language_sentence(sentence: str) -> str:
    r"""Preprocess a natural language sentence w.

    Replace multiple space sequences by one and remove spaces from both ends of the sentence.

    Parameters
    ----------
    sentence : str
        A natural language sentence.

    Returns
    -------
    str
        The preprocessed sentence.
    """
    s = sentence
    s = re.sub(r" +", " ", s)
    s = s.strip()
    return s


def preprocess_sparql_file_base(
    input_file_path: Union[str, os.PathLike, Path],
    output_file_path: Union[str, os.PathLike, Path, None] = None,
    checkpointing_period: int = 10,
    *,
    encoder: Callable[[str], str],
) -> Path:
    r"""Preprocess a SPARQL file.

    Parameters
    ----------
    input_file_path : str, os.PathLike or Path
        The path of the file to preprocess.
    output_file_path : str, os.PathLike or Path, optional
        The path of the final preprocessed file. The file is created if it does not exist or overwritten if it already
        exists. If None, defaults to "preprocessed_data_files/<input_file_name>" where <input_file_name> is the name of
        the input-file.
    checkpointing_period : int, optional
        For every checkpointing_period of processed examples, the examples are stored in
        <output_file_path>.checkpoint_data and the algorithm state in <checkpoint_data>.checkpoint_state. If the
        algorithm is interrupted, it can be resumed from the checkpoint by calling it with the same arguments. Defaults
        to 10.
    encoder : Callable[[str], str]
        The encoding function.

    Returns
    -------
    Path
        The path of the preprocessed file.
    """
    preprocess_sparql = functools.partial(preprocess_sparql_base, encoder=encoder)
    output_file_path = preprocess_file(
        preprocessing_function=preprocess_sparql,
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        checkpointing_period=checkpointing_period,
        progress_bar_description="Amount of preprocessed SPARQLs",
        progress_bar_unit="SPARQL",
    )
    return output_file_path


def preprocess_sparql_base(sparql: str, *, encoder: Callable[[str], str]) -> str:
    r"""Preprocess a SPARQL string.

    Parameters
    ----------
    sparql : str
        The string to be preprocessed.
    encoder : Callable[[str], str]
        The encoding function.

    Returns
    -------
    str
        The preprocessed string.
    """
    s = sparql
    s = do_valid_preprocessing(s)
    s = encoder(s)
    s = s.strip()
    s = re.sub(r" +", " ", s)
    return s


def preprocess_triples_file_base(
    input_file_path: Union[str, os.PathLike, Path],
    output_file_path: Union[str, os.PathLike, Path, None] = None,
    checkpointing_period: int = 10,
    *,
    encoder: Callable[[str], str],
) -> Path:
    r"""Preprocess a triples file.

    Parameters
    ----------
    input_file_path : str, os.PathLike or Path
        The path of the file to preprocess.
    output_file_path : str, os.PathLike or Path, optional
        The path of the final preprocessed file. The file is created if it does not exist or overwritten if it already
        exists. If None, defaults to "preprocessed_data_files/<input_file_name>" where <input_file_name> is the name of
        the input-file.
    checkpointing_period : int, optional
        For every checkpointing_period of processed examples, the examples are stored in
        <output_file_path>.checkpoint_data and the algorithm state in <checkpoint_data>.checkpoint_state. If the
        algorithm is interrupted, it can be resumed from the checkpoint by calling it with the same arguments. Defaults
        to 10.
    encoder : Callable[[str], str]
        The encoding function.

    Returns
    -------
    Path
        The path of the preprocessed file.
    """
    preprocess_triples = functools.partial(preprocess_triples_base, encoder=encoder)
    output_file_path = preprocess_file(
        preprocessing_function=preprocess_triples,
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        checkpointing_period=checkpointing_period,
        progress_bar_description="Amount of preprocessed triple-sets",
        progress_bar_unit="triple-set",
    )
    return output_file_path


def preprocess_triples_base(triples: str, *, encoder: Callable[[str], str]) -> str:
    r"""Preprocess a string of triples.

    The string should not contain new line characters.

    Parameters
    ----------
    triples : str
        The string of triples to be preprocessed.
    encoder : Callable[[str], str]
        The encoding function.

    Returns
    -------
    str
        The preprocessed triples.
    """
    s = triples
    s = upper_bound_literal(s)
    s = preprocess_sparql_base(s, encoder=encoder)
    return s


def do_valid_preprocessing(sparql: str) -> str:
    r"""Preprocessing part which keeps the SPARQL sparql a valid SPARQL.

    Parameters
    ----------
    sparql : str
        String which the preprocessing is done on.

    Returns
    -------
    str
        Preprocessed SPARQL with the same semantic as sparql.

    Todo
    ----
    - uri_to_prefix is no safe SPARQL function. I.e. it might invalidate some SPARQLs or change semantics.
    """
    s = sparql
    s = do_replacements(s, VALID_SPARQL_REPLACEMENTS)
    s = sparql_keyword_to_lower_case(s)
    s = re.sub(
        r"@en", r"@en", s, flags=re.IGNORECASE
    )  # English language tag to lower case.
    s = inline_and_remove_base(s)
    s = inline_and_remove_prefixes(s)
    s = uri_to_prefix(s)
    s = normalize_prefixes(s)
    return s


def inline_and_remove_base(s: str) -> str:
    r"""Inline the BASE IRI of the SPARQL s and remove it.

    Assuming a BASE-IRI is provided. If the IRI of a "<IRI>" occurrence does not start with any scheme in IRI_SCHEME,
    the BASE-IRI is added as prefix.

    Parameters
    ----------
    s : str
        SPARQL string.

    Returns
    -------
    str
        String with inlined and removed BASE.
    """
    match = re.match(r"\s*BASE\s*<([^>]*)>", s, flags=re.IGNORECASE)  # Find BASE-IRI.
    if match is not None:
        base_iri = match.group(1)
        s = re.sub(r"\s*BASE\s*<([^>]*)>", "", s, flags=re.IGNORECASE)  # Remove BASE.
        s = s.lstrip()
        schemes_regex = "|".join(IRI_SCHEMES)
        s = re.sub(f"<(?!({schemes_regex}))([^<>]*)>", f"<{base_iri}\\2>", s)
    return s


def inline_and_remove_prefixes(s: str) -> str:
    r"""Inline the prefixes of the SPARQL s and remove them.

    If multiple URLs are defined for one prefix, inline the last one.


    Parameters
    ----------
    s : str
        SPARQL string.

    Returns
    -------
    str
        String with inlined and removed prefixes.

    Note
    ----
    - We do not substitute prefixes if they follow a '<' because these could be schemas e.g. "bif:".
    - We recognize '.' in prefix-form URIs if they are followed by anything except [\\s,;] e.g. dbr:file.txt. Else, the
      '.' is recognized as "end of triple"-symbol and hence not part of the prefix-form URI.
    """
    empty_prefix_name = False
    empty_prefix_uri = ""
    prefix_url_dict = dict()
    for pre_name, pre_url in re.findall(
        r"PREFIX\s*([^:]*):\s*<([^>]*)>", s, flags=re.IGNORECASE
    ):  # Find prefix.
        s = re.sub(
            f"PREFIX\\s*{pre_name}:\\s*<{pre_url}>", "", s, flags=re.IGNORECASE
        )  # Remove prefix.
        s = s.lstrip()
        prefix_url_dict[pre_name] = pre_url
    for pre_name, pre_url in prefix_url_dict.items():
        if pre_name == "":
            empty_prefix_name = True
            empty_prefix_uri = pre_url
        else:
            s = re.sub(
                f"(?<!<)\\b{pre_name}:((?:[^\\s.,;]|(\\.[^\\s,;]))*)",
                f"<{pre_url}\\1>",
                s,
            )  # Inline prefix.
    if empty_prefix_name:
        # Empty prefix ':<something>' is replaced by its URI if it is preceded by a whitespace or a SPARQL term
        # delimiter ('.', ',', ';').
        s = re.sub(
            "([.,;\\s]):((?:[^\\s.,;]|(\\.[^\\s,;]))*)",
            f"\\1<{empty_prefix_uri}\\2>",
            s,
        )
    return s


def normalize_prefixes(s: str) -> str:
    r"""Replace some prefixes with equivalent ones defined in PREFIX_EQUIVALENTS.

    All entries in one row are replaced by the last row element.

    Parameters
    ----------
    s : str
        The string where the replacing is done

    Returns
    -------
    str
        The string with replacements.
    """
    for row in PREFIX_EQUIVALENTS:
        encoding = row[-1]
        for elem in row[:-1]:
            s = re.sub(elem, encoding, s)
    return s


def upper_bound_literal(triples_example: str, max_literal_length: int = 60) -> str:
    r"""If a literal exceeds the max_literal_length, truncate to max_literal_length.

    Parameters
    ----------
    triples_example : str
        The triples where literals are truncated.
    max_literal_length : int, optional
        The number of chars at which literals are truncated. Defaults to 60 which are around six long words.

    Returns
    -------
    str
        String with truncated literals.
    """

    def truncate_match(match: re.Match) -> str:
        r"""Truncate match.

        Parameters
        ----------
        match : re.Match
            The Match found by re.sub.

        Returns
        -------
        str
            The replacement string.
        """
        whole_match = match.group(0)
        if match.group(1) is not None:
            literal = match.group(1)
            quotation = '"""'
        elif match.group(2) is not None:
            literal = match.group(2)
            quotation = "'''"
        elif match.group(3) is not None:
            literal = match.group(3)
            quotation = '"'
        elif match.group(4) is not None:
            literal = match.group(4)
            quotation = "'"
        else:  # Escape through <>.
            return whole_match
        if len(literal) > max_literal_length:
            return quotation + literal[:max_literal_length] + quotation
        return whole_match

    s = triples_example
    # <> escapes quotation marks.
    s = re.sub(
        r"<[^<>]*>|"
        r'"""(.*?)"""|'
        r"'''(.*?)'''|"
        r'"((?:\\.|[^"\\])*)"|'
        r"'((?:\\.|[^'\\])*)'",
        truncate_match,
        s,
    )
    return s


def uri_to_prefix(s: str) -> str:
    r"""Substitute the default SPARQL URIs and the "https://" versions with their prefixes.

    PREFIX_TO_URI defines the substitutions to be done. Each URI with a prefix "http://" is also considered with the
    prefix "https://".

    Parameters
    ----------
    s : str
        string where the substitution is made.

    Returns
    -------
    str
        The string with substituted URIs.

    Note
    ----
    - DBpedia does not allow prefixes to be used while the remainder of the URI still carries a '/'. SPARQL allows it,
      and we benefit also from allowing it.
    - We do allow special characters like '(', ')', '&', '|', '.' in the prefix-form URI to make it shorter. This is
      not allowed by SPARQL. So this function might invalidate the SPARQL or change semantics.
    """
    for prefix, uri in PREFIX_TO_URI.items():
        s = re.sub(f"<{uri}([^>]*)>", f"{prefix}\\1", s)

    for https_uri, prefix in HTTPS_URI_TO_PREFIX.items():
        s = re.sub(f"<{https_uri}([^>]*)>", f"{prefix}\\1", s)
    return s


def prefix_to_uri(s: str) -> str:
    r"""Substitute default DBpedia prefixes by their URI.

    PREFIX_TO_URI defines the substitutions to be done. The key is substituted by the value and chevrons are put around.

    Parameters
    ----------
    s : str
        string where the substitution is made.

    Returns
    -------
    str
        The string with prefixes substituted by URIs.

    Note
    ----
    - We do not substitute prefixes if they follow a '<' because these could be schemas e.g. "bif:".
    - We recognize '.' in prefix-form URIs if they are followed by anything except [\\s,;] e.g. dbr:file.txt. Else, the
      '.' is recognized as "end of triple"-symbol and hence not part of the prefix-form URI.
    """
    for prefix, substitute in PREFIX_TO_URI.items():
        s = re.sub(
            f"(?<!<)\\b{prefix}((?:[^\\s.,;]|(\\.[^\\s,;]))*)", f"<{substitute}\\1>", s
        )
    return s


def sparql_keyword_to_lower_case(s: str) -> str:
    r"""Convert all SPARQL keywords from SPARQL_KEYWORDS in s to lower case.

    Parameters
    ----------
    s : str
        The string where keywords are converted.

    Returns
    -------
    str
        The string with converted keywords.
    """
    keyword_regex = "|".join(SPARQL_KEYWORDS)
    s = re.sub(
        f"\\s*\\b({keyword_regex})\\b\\s*", r" \1 ", s
    )  # Put one space around each found upper case keyword.

    normalize_s = []
    for token in s.split():
        beginning_subtoken_match = re.search(r"^\w+", token)
        if beginning_subtoken_match is not None:
            beginning_subtoken = beginning_subtoken_match.group()
            if beginning_subtoken.upper() in SPARQL_KEYWORDS:
                token = re.sub(r"^\w+", beginning_subtoken.lower(), token)
        normalize_s.append(token)
    s = " ".join(normalize_s)
    return s


def do_replacements(
    s: str, replacements: list[list[str]], remove_successive_whitespaces: bool = True
) -> str:
    r"""Replace string occurrences in s by some replacement.

    For each row in replacements, replace each column entry, except the last one, by the second to last column entry.

    Parameters
    ----------
    s : str
        Some string.
    replacements : list[list[str]]
        Specifies the replacements. Each entry, except for the last one, is replaced by the second to last one.
    remove_successive_whitespaces : bool, optional
        If true, remove successive whitespaces in output. Defaults to True.

    Returns
    -------
    str
        The string s with replacements.
    """
    for r in replacements:
        encoding = r[-2]
        for original in r[:-2]:
            s = s.replace(original, encoding)
    if remove_successive_whitespaces:
        s = re.sub(r" +", " ", s)
    return s


def revert_replacements(
    s: str, replacements: list[list[str]], remove_successive_whitespaces: bool = True
) -> str:
    r"""Replace parts of s specified by replacements.

    For each row in replacements, replace the second to last column entry by the last column entry.

    Parameters
    ----------
    s : str
        The string where the replacement is done.
    replacements : list[list[str]]
        Specifies the replacements. The second to last entry is replaced by the last one.
    remove_successive_whitespaces : bool, optional
        If true, remove successive whitespaces in output. Defaults to True.

    Returns
    -------
    str
        s with replacements.
    """
    for r in replacements:
        encoding = r[-2]
        decoding = r[-1]
        s = s.replace(encoding, decoding)
    if remove_successive_whitespaces:
        s = re.sub(r" +", " ", s)
    return s


def encode_asterisk(s: str) -> str:
    r"""Replace '*' by " all variables " when it is used for selecting all variables.

    Parameters
    ----------
    s : str
        The string where the replacement is done.

    Returns
    -------
    str
        The string with replacements.
    """
    s = re.sub(
        r"((SELECT\s*(DISTINCT|REDUCED)?)|DESCRIBE)\s*\*",
        r"\1 all variables ",
        s,
        flags=re.IGNORECASE,
    )
    s = re.sub(r" +", " ", s)
    return s


def decode_asterisk(s: str) -> str:
    r"""Replace " all variables " by ' * ' when it is used for selecting all variables.

    Parameters
    ----------
    s : str
        The string where the replacement is done.

    Returns
    -------
    str
        The string with replacements.
    """
    s = re.sub(
        r"((SELECT\s*(DISTINCT|REDUCED)?)|DESCRIBE)\s*all variables",
        r"\1 * ",
        s,
        flags=re.IGNORECASE,
    )
    s = re.sub(r" +", " ", s)
    return s


def encode_datatype(s: str) -> str:
    r"""Encode "^^" with " datatype ".

    Parameters
    ----------
    s : str
        The string were datatypes are encoded.

    Returns
    -------
    str
        The encoded string s.
    """
    s = s.replace("^^", " datatype ")
    return s


def decode_datatype(s: str) -> str:
    r"""Decode " datatype " to "^^" such that the SPARQL keyword "datatype" is not decoded.

    The SPARQL keyword DATATYPE can also be written in lowercase, so we have two kinds of datatype in our encoded
    sparql.

    Parameters
    ----------
    s : str
        The string where datatypes should be decoded.

    Returns
    -------
    str
        The decoded string.
    """
    s = re.sub(r"(\"\"\"|\'\'\'|\"|\') datatype ", r"\1^^", s)
    return s


def decode_file_base(
    input_file_path: Union[str, os.PathLike, Path],
    output_file_path: Union[str, os.PathLike, Path, None] = None,
    checkpointing_period: int = 10,
    *,
    decoder: Callable[[str], str],
) -> Path:
    r"""Decode a file of encoded SPARQLs.

    Parameters
    ----------
    input_file_path : str, os.PathLike or Path
        The path to the file of encoded SPARQLs.
    output_file_path : str, os.PathLike or Path, optional
        The path of the decoded SPARQLs. The file is created if it does not exist or overwritten if it already exists.
        If None, defaults to "decoded_files/<input_file_name>" where <input_file_name> is the name of the input-file.
    checkpointing_period : int, optional
        For every checkpointing_period of decoded examples, the examples are stored in
        <output_file_path>.checkpoint_data and the algorithm state in <checkpoint_data>.checkpoint_state. If the
        algorithm is interrupted, it can be resumed from the checkpoint by calling it with the same arguments. Defaults
        to 10.
    decoder : Callable[[str], str]
        The decoding function.

    Returns
    -------
        The path of the decoded file.
    """
    input_file_path = Path(input_file_path)
    if output_file_path is None:
        output_file_path = Path("decoded_files") / input_file_path.name
    else:
        output_file_path = Path(output_file_path)
    output_file_path = preprocess_file(
        preprocessing_function=decoder,
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        checkpointing_period=checkpointing_period,
        progress_bar_description="Amount of decoded SPARQLs",
        progress_bar_unit="SPARQL",
    )
    return output_file_path


def sparql_encoder_levenshtein_dist_on_file_base(
    input_file_path: Union[str, os.PathLike, Path],
    log_lower_bound: float = math.inf,
    *,
    encoder: Callable[[str], str],
    decoder: Callable[[str], str],
) -> float:
    r"""Preprocess the given data and then calculate the Levenshtein distance between encoding and decoding it.

    The SPARQL preprocessing part is applied for preprocessing.

    Parameters
    ----------
    input_file_path : str, os.PathLike or Path
        A path-like object to the file with the SPARQLs.
    log_lower_bound : float, optional
        Print logging information to stdout for each example which has an equal or higher Levenshtein distance than
        log_lower_bound. Defaults to infinity.
    encoder : Callable[[str], str]
        The encoding function.
    decoder : Callable[[str], str]
        The decoding function.

    Returns
    -------
    float
        The mean Levenshtein distance.
    """
    input_file_path = Path(input_file_path)
    cumulative_dist = 0.0
    amount = 0
    with open(input_file_path, "r", encoding="utf-8") as file:
        for sparql in tqdm(file, desc="Amount of scored SPARQLs", unit="SPARQL"):
            dist = sparql_encoder_levenshtein_dist_base(
                sparql.strip(),
                log_lower_bound=log_lower_bound,
                encoder=encoder,
                decoder=decoder,
            )
            cumulative_dist += dist
            amount += 1
    mean_dist = cumulative_dist / amount
    return mean_dist


def sparql_encoder_levenshtein_dist_base(
    sparql: str,
    log_lower_bound: float = math.inf,
    *,
    encoder: Callable[[str], str],
    decoder: Callable[[str], str],
) -> float:
    r"""Preprocess sparql and then calculate the Levenshtein distance between encoding and decoding it.

    The SPARQL preprocessing part is applied for preprocessing.

    Parameters
    ----------
    sparql : str
        A SPARQL string.
    log_lower_bound : float, optional
        Print logging information to stdout for each example which has an equal or higher Levenshtein distance than
        log_lower_bound. Defaults to infinity.
    encoder : Callable[[str], str]
        The encoding function.
    decoder : Callable[[str], str]
        The decoding function.

    Returns
    -------
    float
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
        print("\nDifference:\n")
        diff = ndiff(preprocessed_normalized.split(), decoded.split())
        print("\n".join(diff))
        print(f"\nDistance: {dist}")
        print("----------------------------------------------------")
    return dist


def test_do_valid_preprocessing_on_file(
    input_file_path: Union[str, os.PathLike, Path]
) -> tuple[float, int]:
    r"""Test the function do_valid_preprocessing on SPARQLs in input_file_path.

    Parameters
    ----------
    input_file_path : str, os.PathLike or Path
        A path-like object to the file with the SPARQLs.

    Returns
    -------
    tuple[float, str]:
        float: The ratio of valid preprocessed SPARQLs to all SPARQLs which were valid before preprocessing.
        str: The number of not valid unprocessed SPARQLs.
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
    print(
        f"Number of not valid SPARQLs before preprocessing: {num_unprocessed_not_valid}"
    )
    print(
        f"Ratio between valid and all SPARQLs which were valid before preprocessing: {ratio}"
    )
    return ratio, num_unprocessed_not_valid


def test_do_valid_preprocessing(sparql: str) -> int:
    r"""Test the function do_valid_preprocessing on SPARQL sparql.

    Parameters
    ----------
    sparql : str
        SPARQL on which the preprocessing is done in.

    Returns
    -------
    int
        1, if the preprocessing is valid. 0, if it is not valid. -1, if the unprocessed SPARQL is not valid.
    """
    preprocessed_sparql = do_valid_preprocessing(sparql)

    # Query SPARQL
    SPARQL_WRAPPER.setQuery(sparql)
    try:
        SPARQL_WRAPPER.queryAndConvert()
    except BaseException as exception:
        print("\n--------------------------------------------------")
        print(f"An exception occurred at unprocessed SPARQL:\n{sparql}")
        print(f"Exception:\n{exception}")
        print("----------------------------------------------------")
        return -1

    # Query Preprocessed SPARQL
    SPARQL_WRAPPER.setQuery(preprocessed_sparql)
    try:
        SPARQL_WRAPPER.queryAndConvert()
    except BaseException as exception:
        print("\n--------------------------------------------------")
        print(f"An exception occurred at preprocessed SPARQL:\n{preprocessed_sparql}")
        print(f"Exception:\n{exception}")
        print(f"The corresponding unprocessed SPARQL is:\n{sparql}")
        print("----------------------------------------------------")
        return 0
    return 1


def split_qtq_uniformly(
    input_file_path: Union[str, os.PathLike, Path],
    output_folder_path: Union[str, os.PathLike, Path] = "split_data_files",
    validation_set_portion: float = 0.2,
) -> tuple[Path, Path]:
    r"""Split a qtq-file into a training and validation file.

    The validation file has the size of the input file times the validation_set_portion. The training file the
    respective remainder.
    Let <input_file_name>.json be the input file. Then we store the validation file in
    <output_folder_path>/<input_file_name>.val.json and the training file in
    <output_folder_path>/<input_file_name>.train.json.

    Parameters
    ----------
    input_file_path : str, os.PathLike or Path
        The path to the input file. Suffix must be ".json".
    output_folder_path: str, os.PathLike or Path, optional
        The path where the split qtq-file parts should be stored. Defaults to "split_data_files".
    validation_set_portion: float, optional
        The portion of the input_file which is stored in the validation file. Defaults to 0.2.

    Returns
    -------
    tuple of Path, Path with elements:
        - Path to the validation file.
        - Path to the training file.
    """
    input_file_path = Path(input_file_path)
    output_folder_path = Path(output_folder_path)
    if input_file_path.suffix != ".json":
        raise ValueError('input_file_path should be ending with ".json"')
    output_folder_path.mkdir(parents=True, exist_ok=True)
    val_file_path = output_folder_path / input_file_path.with_suffix(".val.json").name
    train_file_path = (
        output_folder_path / input_file_path.with_suffix(".train.json").name
    )
    with open(val_file_path, "w", encoding="utf-8") as val_file, open(
        train_file_path, "w", encoding="utf-8"
    ) as train_file, open(input_file_path, "r", encoding="utf-8") as input_file:
        data_json = json.load(input_file)
        questions = data_json["questions"]
        random.shuffle(questions)
        val_set_size = math.floor(validation_set_portion * len(questions))
        val_questions = questions[:val_set_size]
        train_questions = questions[val_set_size:]
        val_dict = {"questions": val_questions}
        train_dict = {"questions": train_questions}
        json.dump(obj=val_dict, fp=val_file)
        json.dump(obj=train_dict, fp=train_file)
    return val_file_path, train_file_path


def split_preprocessed_files(
    input_file_paths: list[Union[str, os.PathLike, Path]],
    output_folder_path: Union[str, os.PathLike, Path] = "split_data_files",
    validation_set_portion: float = 0.2,
) -> Union[tuple[Path, Path], None]:
    r"""Split qtq-files into training and validation files at the same indexes.

    The validation file has the size of the input file times the validation_set_portion. The training file the
    respective remainder.
    The length of the files have to be the same.
    The files must not have the same name.
    Let <input_file_name> be the name of some input file. Then we store the validation file in
    <output_folder_path>/<input_file_name>.val and the training file in
    <output_folder_path>/<input_file_name>.train.

    Parameters
    ----------
    input_file_paths : list of str, os.PathLike or Path
        The paths to the input files.
    output_folder_path: str, os.PathLike or Path, optional
        The path where the split qtq-files are stored. Defaults to "split_data_files".
    validation_set_portion: float, optional
        The portion of the input_file which is stored in the validation file. Defaults to 0.2.

    Returns
    -------
    None
    """
    input_file_paths_: list[Path] = list()
    for i, path in enumerate(input_file_paths):
        input_file_paths_[i] = Path(path)
    output_folder_path = Path(output_folder_path)
    output_folder_path.mkdir(parents=True, exist_ok=True)

    num_examples = 0
    with open(input_file_paths_[0], "r", encoding="utf-8") as file:
        for example in file:
            num_examples += 1

    val_size = math.floor(validation_set_portion * num_examples)
    val_indexes = random.sample(population=range(num_examples), k=val_size)
    mask = np.full(num_examples, False, dtype=bool)
    mask[val_indexes] = True

    for input_file_path in input_file_paths_:
        with open(input_file_path, "r", encoding="utf-8") as file:
            all_examples = np.array([example for example in file])
        if len(all_examples) != num_examples:
            print("The provided files do not have the same number of examples (lines).")
            return None
        val_examples = all_examples[mask]
        train_examples = all_examples[~mask]
        val_file_path = output_folder_path / (input_file_path.name + ".val")
        with open(val_file_path, "w", encoding="utf-8") as file:
            for example in val_examples:
                file.write(example)
        train_file_path = output_folder_path / (input_file_path.name + ".train")
        with open(train_file_path, "w", encoding="utf-8") as file:
            for example in train_examples:
                file.write(example)
    return None
