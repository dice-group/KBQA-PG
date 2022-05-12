"""Preprocess questions, SPARQLs and triples and decode predicted SPARQLs with the overhauled preprocessor."""
import functools
import math
import os
import re
from tqdm import tqdm
from pathlib import Path
import distance
from difflib import ndiff

from typing import Union

from KBQA.appB.preprocessing import utils
from KBQA.appB.preprocessing.utils import preprocess_qtq_file_base
from KBQA.appB.preprocessing.utils import preprocess_natural_language_file as preprocess_natural_language_file_
from KBQA.appB.preprocessing.utils import preprocess_natural_language_sentence as preprocess_natural_language_sentence_
from KBQA.appB.preprocessing.utils import preprocess_sparql_file_base
from KBQA.appB.preprocessing.utils import preprocess_sparql_base
from KBQA.appB.preprocessing.utils import preprocess_triples_file_base
from KBQA.appB.preprocessing.utils import preprocess_triples_base
from KBQA.appB.preprocessing.utils import do_replacements
from KBQA.appB.preprocessing.utils import revert_replacements
from KBQA.appB.preprocessing.utils import encode_asterisk
from KBQA.appB.preprocessing.utils import decode_asterisk
from KBQA.appB.preprocessing.utils import encode_datatype
from KBQA.appB.preprocessing.utils import decode_datatype
from KBQA.appB.preprocessing.utils import decode_file_base
from KBQA.appB.preprocessing.utils import sparql_encoder_levenshtein_dist_on_file_base
from KBQA.appB.preprocessing.utils import sparql_encoder_levenshtein_dist_base
from KBQA.appB.preprocessing.utils import prefix_to_uri
from KBQA.appB.preprocessing.utils import uri_to_prefix
from KBQA.appB.preprocessing.utils import normalize_prefixes

ENCODING_REPLACEMENTS = utils.ENCODING_REPLACEMENTS


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

    Note:
        Checkpointing is not applied on the data-separation step.
    """
    return preprocess_qtq_file_base(input_file_path,
                                    output_folder_path,
                                    keep_separated_input_file,
                                    separated_input_files_folder_path,
                                    checkpointing_period,
                                    encoder=encode)


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
    return preprocess_natural_language_file_(input_file_path,
                                             output_file_path,
                                             checkpointing_period)


def preprocess_natural_language_sentence(w):
    return preprocess_natural_language_sentence_(w)


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
    return preprocess_sparql_file_base(input_file_path,
                                       output_file_path,
                                       checkpointing_period,
                                       encoder = encode)


def preprocess_sparql(s: str) -> str:
    """Preprocess a SPARQL string.

    Args:
        s: The string to be preprocessed.

    Returns:
        The preprocessed string.
    """
    return preprocess_sparql_base(s, encoder=encode)


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
    return preprocess_triples_file_base(input_file_path,
                                        output_file_path,
                                        checkpointing_period,
                                        encoder=encode)


def preprocess_triples(triples_example):
    """Preprocess a string of triples.

    The string should not contain new line characters.

    Args:
        triples_example: The string of triples to be preprocessed.

    Returns:
        The preprocessed triples string.
    """
    return preprocess_triples_base(triples_example, encoder=encode)


def encode(sparql):
    """Encode sparql.

    sparql will not be a valid SPARQL query afterwards and has to be decoded by decode() to make it valid again.
    """
    s = sparql
    s = uri_to_prefix(s)
    s = normalize_prefixes(s)
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
    s = prefix_to_uri(s)
    s = s.strip()
    s = re.sub(r" +", " ", s)
    return s


def decode_file(file_path: Union[str, os.PathLike, Path]) -> list[str]:
    """Decode a file of encoded SPARQLs.

    Args:
        file_path: The path to the file of encoded SPARQLs.

    Returns:
        A list of the decoded SPARQLs.
    """
    return decode_file_base(file_path, decoder=decode)


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
    return sparql_encoder_levenshtein_dist_on_file_base(input_file_path,
                                                        log_lower_bound,
                                                        encoder=encode,
                                                        decoder=decode)


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
    return sparql_encoder_levenshtein_dist_base(sparql, log_lower_bound, encoder=encode, decoder=decode)
