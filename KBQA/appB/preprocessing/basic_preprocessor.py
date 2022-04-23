"""Preprocess questions, SPARQLs and triples and decode predicted SPARQLs with the overhauled preprocessor."""
import math
import os
import re
from pathlib import Path
import distance
from difflib import ndiff

from typing import Union

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
from KBQA.appB.preprocessing.utils import sparql_encoder_levenshtein_dist_on_file

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
    s = s.strip()
    s = re.sub(r" +", " ", s)
    return s


def decode(encoded_sparql):
    """"Decode encoded sparql to make it a valid sparql query again."""
    s = encoded_sparql
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


def sparql_encoder_levenshtein_dist(sparql: str, log_lower_bound: float = math.inf) -> float:
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
