"""Module to post process sparql."""

from app.t5.utils import decode_datatype
from app.t5.utils import decode_asterisk
from app.t5.utils import revert_replacements
from app.t5.utils import prefix_to_uri
#import app.t5.utils
from app.t5.utils import ENCODING_REPLACEMENTS

#ENCODING_REPLACEMENTS = utils.ENCODING_REPLACEMENTS

import re



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