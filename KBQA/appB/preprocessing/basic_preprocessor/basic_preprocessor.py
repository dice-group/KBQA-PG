r"""Preprocess questions, SPARQLs and triples and decode predicted SPARQLs with the overhauled preprocessor."""
import math
import os
from pathlib import Path
import re
from typing import Union

from KBQA.appB.preprocessing import utils
from KBQA.appB.preprocessing.utils import decode_asterisk
from KBQA.appB.preprocessing.utils import decode_datatype
from KBQA.appB.preprocessing.utils import decode_file_base
from KBQA.appB.preprocessing.utils import do_replacements
from KBQA.appB.preprocessing.utils import encode_asterisk
from KBQA.appB.preprocessing.utils import encode_datatype
from KBQA.appB.preprocessing.utils import normalize_prefixes
from KBQA.appB.preprocessing.utils import prefix_to_uri
from KBQA.appB.preprocessing.utils import preprocess_natural_language_file as preprocess_natural_language_file_
from KBQA.appB.preprocessing.utils import preprocess_natural_language_sentence as preprocess_natural_language_sentence_
from KBQA.appB.preprocessing.utils import preprocess_qtq_file_base
from KBQA.appB.preprocessing.utils import preprocess_sparql_base
from KBQA.appB.preprocessing.utils import preprocess_sparql_file_base
from KBQA.appB.preprocessing.utils import preprocess_triples_base
from KBQA.appB.preprocessing.utils import preprocess_triples_file_base
from KBQA.appB.preprocessing.utils import revert_replacements
from KBQA.appB.preprocessing.utils import sparql_encoder_levenshtein_dist_base
from KBQA.appB.preprocessing.utils import sparql_encoder_levenshtein_dist_on_file_base
from KBQA.appB.preprocessing.utils import uri_to_prefix

ENCODING_REPLACEMENTS = utils.ENCODING_REPLACEMENTS


def preprocess_qtq_file(
    input_file_path: Union[str, os.PathLike, Path],
    output_folder_path: Union[str, os.PathLike, Path] = Path("preprocessed_data_files"),
    keep_separated_input_file: bool = False,
    separated_input_files_folder_path: Union[str, os.PathLike, Path] = Path(
        "separated_data_files"
    ),
    checkpointing_period: int = 10,
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
    return preprocess_qtq_file_base(
        input_file_path,
        output_folder_path,
        keep_separated_input_file,
        separated_input_files_folder_path,
        checkpointing_period,
        encoder=encode,
    )


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
    return preprocess_natural_language_file_(
        input_file_path, output_file_path, checkpointing_period
    )


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
    return preprocess_natural_language_sentence_(sentence)


def preprocess_sparql_file(
    input_file_path: Union[str, os.PathLike, Path],
    output_file_path: Union[str, os.PathLike, Path, None] = None,
    checkpointing_period: int = 10,
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

    Returns
    -------
    Path
        The path of the preprocessed file.
    """
    return preprocess_sparql_file_base(
        input_file_path, output_file_path, checkpointing_period, encoder=encode
    )


def preprocess_sparql(sparql: str) -> str:
    r"""Preprocess a SPARQL string.

    Parameters
    ----------
    sparql : str
        The string to be preprocessed.

    Returns
    -------
    str
        The preprocessed string.
    """
    return preprocess_sparql_base(sparql, encoder=encode)


def preprocess_triples_file(
    input_file_path: Union[str, os.PathLike, Path],
    output_file_path: Union[str, os.PathLike, Path, None] = None,
    checkpointing_period: int = 10,
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

    Returns
    -------
    Path
        The path of the preprocessed file.
    """
    return preprocess_triples_file_base(
        input_file_path, output_file_path, checkpointing_period, encoder=encode
    )


def preprocess_triples(triples: str) -> str:
    r"""Preprocess a string of triples.

    The string should not contain new line characters.

    Parameters
    ----------
    triples : str
        The string of triples to be preprocessed.

    Returns
    -------
    str
        The preprocessed triples.
    """
    return preprocess_triples_base(triples, encoder=encode)


def encode(sparql: str) -> str:
    r"""Encode sparql.

    sparql will not be a valid SPARQL query afterwards and has to be decoded by decode() to make it valid again.

    Parameters
    ----------
    sparql : str
        Encode this string.

    Returns
    -------
    str
        Return encoded string.
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


def decode(encoded_sparql: str) -> str:
    r"""Decode encoded sparql to make it a valid sparql query again.

    Parameters
    ----------
    encoded_sparql : str
        Decode this string.

    Returns
    -------
    str
        The decoded string.
    """
    s = encoded_sparql
    s = decode_datatype(s)
    s = decode_asterisk(s)
    s = revert_replacements(
        s, ENCODING_REPLACEMENTS, remove_successive_whitespaces=False
    )
    s = prefix_to_uri(s)
    s = s.strip()
    s = re.sub(r" +", " ", s)
    return s


def decode_file(
    input_file_path: Union[str, os.PathLike, Path],
    output_file_path: Union[str, os.PathLike, Path, None] = None,
    checkpointing_period: int = 10,
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

    Returns
    -------
        The path of the decoded file.
    """
    return decode_file_base(
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        checkpointing_period=checkpointing_period,
        decoder=decode,
    )


def sparql_encoder_levenshtein_dist_on_file(
    input_file_path: Union[str, os.PathLike, Path], log_lower_bound: float = math.inf
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

    Returns
    -------
    float
        The mean Levenshtein distance.
    """
    return sparql_encoder_levenshtein_dist_on_file_base(
        input_file_path, log_lower_bound, encoder=encode, decoder=decode
    )


def sparql_encoder_levenshtein_dist(
    sparql: str, log_lower_bound: float = math.inf
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

    Returns
    -------
    float
        The Levenshtein distance.
    """
    return sparql_encoder_levenshtein_dist_base(
        sparql, log_lower_bound, encoder=encode, decoder=decode
    )
