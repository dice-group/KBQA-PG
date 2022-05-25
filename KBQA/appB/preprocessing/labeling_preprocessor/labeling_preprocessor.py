"""Preprocess questions, SPARQLs and triples with labeling approach and decode correspondingly."""
import math
import os
import re
from pathlib import Path

from typing import Union

from KBQA.appB.summarizers.utils import query_dbspotlight
from KBQA.appB.summarizers.utils import query_tagme
from KBQA.appB.summarizers.utils import query_falcon
from KBQA.appB.summarizers.utils import get_uri_for_wiki_page_id

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
from KBQA.appB.preprocessing.utils import uri_to_prefix
from KBQA.appB.preprocessing.utils import prefix_to_uri
from KBQA.appB.preprocessing.utils import normalize_prefixes
from KBQA.appB.preprocessing.utils import encode_asterisk
from KBQA.appB.preprocessing.utils import decode_asterisk
from KBQA.appB.preprocessing.utils import encode_datatype
from KBQA.appB.preprocessing.utils import decode_datatype
from KBQA.appB.preprocessing.utils import decode_file_base
from KBQA.appB.preprocessing.utils import sparql_encoder_levenshtein_dist_on_file_base
from KBQA.appB.preprocessing.utils import sparql_encoder_levenshtein_dist_base

SPARQL_WRAPPER = utils.SPARQL_WRAPPER
ENCODING_REPLACEMENTS = utils.ENCODING_REPLACEMENTS
PREFIX_TO_URI = utils.PREFIX_TO_URI


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
                                       encoder=encode)


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
    s = prefix_to_uri(s)
    s = s.strip()
    s = re.sub(r" +", " ", s)
    return s


def decode_file(input_file_path: Union[str, os.PathLike, Path],
                output_file_path: Union[str, os.PathLike, Path, None] = None,
                checkpointing_period: int = 10) -> Path:
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

    Returns:
        The path of the decoded file.
    """
    return decode_file_base(input_file_path=input_file_path,
                            output_file_path=output_file_path,
                            checkpointing_period=checkpointing_period,
                            decoder=decode)


def encode_uri_by_label(s: str) -> str:
    """Replace "<prefix:><path>" by "<prefix:> <label_of_the_corresponding_URI> :end_label".

    ":end_label" should be part of the tokenizer vocabulary.
    Excluded prefixes are: "xsd:". "xsd:" usually provides labels but these are less natural language related.

    Args:
        s: String where the encoding is done.

    Returns:
        String after encoding.
    """
    excluded = ["xsd:"]
    prefixes = list(PREFIX_TO_URI.keys())
    prefixes = [elem for elem in prefixes if elem not in excluded]
    for prefix in prefixes:
        s = re.sub(f"\\b({prefix})(([^\\s.,;]|(\\.[^\\s,;]))*)", generate_label_encoding, s)
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
    prefix = match.group(1)
    path = match.group(2)
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
    """Replace "<prefix:> <label_of_the_corresponding_URI> :end_label" by "'<'<corresponding_uri>'>'".

    ":end_label" should be part of the tokenizer vocabulary.
    """
    initial_s = s
    s = decode_label_with_mapping(s)
    s = decode_label_with_entity_linking(s, context=initial_s)
    return s


def decode_label_with_mapping(s: str) -> str:
    """Replace a label with a uri from mapping the label back to the corresponding entity in DBpedia.

    Replace "<prefix:> <label_of_the_corresponding_URI> :end_label" by "'<'<corresponding_uri>'>'".
    Excluded prefixes are: "xsd:". This holds for encoding respectively.

    Args:
        s: The string where labels should be decoded.

    Returns:
        A string with decoded labels if some were found.
    """
    excluded = ["xsd:"]
    prefixes = list(PREFIX_TO_URI.keys())
    prefixes = [elem for elem in prefixes if elem not in excluded]
    prefixes_regex = '|'.join(prefixes)
    s = re.sub(f"((?:a )?)\\b({prefixes_regex})(?!{prefixes_regex})((?:.(?!\\b({prefixes_regex})))*?):end_label",
               generate_label_decoding, s)
    return s


def generate_label_decoding(match):
    """Generate the string for "<prefix:> <label_of_the_corresponding_URI> :end_label" which is
    "'<'<corresponding_uri>'>'".

    Only supports english labels, i.e. "<label>"@en.
    We might have multiple results e.g. http://dbpedia.org/resource/Category:Skype and
    http://dbpedia.org/resource/Skype. We decide on using the shortest in these cases.
    We might have multiple results e.g. http://dbpedia.org/ontology/Publisher or http://dbpedia.org/ontology/publisher.
    We always choose the lower case suffix here, which is "publisher" in this case. An exception for this rule is, if
    the URI is preceded by a prior "a". Then we choose the upper case, "Publisher" in our example. This is, because
    upper case usually correspond to a class and "a" indicates that a class is needed.
    Sometimes, the suffix of a URI contains no ASCII e.g. for the label "writer" we get URIs with suffixes "Writer",
    "writer" and "<something in non ASCII chars>". If at least one URI with a suffix which contains ASCII exists, we
    will choose this one over each URI where the suffix does not contain any ASCII.

    Args:
        match: A re.Match object.

    Returns:
        string: Some "'<'<corresponding_uri>'>'" if a uri is found. Else an empty string "".
    """
    has_prior_a = match.group(1) == "a "
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
        uris = [binding["uri"]["value"] for binding in bindings]
        uris = _remove_uris_with_no_ascii_in_suffix(uris=uris)
        if has_prior_a:
            uris.sort(reverse=False)  # If we have a type URI, upper case first.
        else:
            uris.sort(reverse=True)  # Lower case first.
        uris.sort(key=len)
        uri = uris[0]

    if uri is None:
        whole_match = match.group(0)
        return whole_match
    return match.group(1) + "<" + uri + ">"


def _remove_uris_with_no_ascii_in_suffix(uris: list[str]) -> list[str]:
    """Remove URIs from uris where the suffix does not contain any ASCII.

    Sometimes, the suffix of a URI contains no ASCII e.g. for the label "writer" we get URIs with suffixes "Writer",
    "writer" and "<something in non ASCII chars>". This function sorts the last on out.

    Parameters
    ----------
    uris : list of str
        The URIs.

    Returns
    -------
    list of str
        The URIs without ones which have no ASCII

    Note
    ----
        Only remove URIs, if at least one URI with an ASCII in the suffix exists.
    """
    no_ascii = list()
    at_least_one_ascii = False
    for uri in uris:
        suffix = uri.rsplit(sep='/', maxsplit=1)[-1]
        match = re.search(pattern=r"\w", string=suffix, flags=re.ASCII)
        if len(suffix) == 0:
            no_ascii.append(False)
            at_least_one_ascii = True
        elif match is None:
            no_ascii.append(True)
        else:
            no_ascii.append(False)
            at_least_one_ascii = True
    new_uris = list()
    if at_least_one_ascii:
        for uri, no_ascii_in_uri in zip(uris, no_ascii):
            if not no_ascii_in_uri:
                new_uris.append(uri)
    return new_uris


def decode_label_with_entity_linking(s: str, context: str, *, confidence: float = 0.1) -> str:
    """Replace a label with a uri found by entity- or relation-linking.

    Replace "<prefix:> <label_of_the_corresponding_URI> :end_label" by "'<'<corresponding_uri>'>'".
    Excluded prefixes are: "xsd:". This holds for encoding respectively.
    We might find URIs for the label string only or the string consisting of prefix and label. We also get scores
    for each found URI. We prioritize the found ones in the following order.
    1. Found for label, and the URI has the same prefix as the one preceding our label.
    2. Found for prefix and label, and the URI has the same prefix as the one preceding our label.
    3. Found for label.
    4. Found for prefix and label.
    If multiple URIs fulfill some point, the one with the highest score is chosen.
    We suggest a confidence of 0.1 as it finds as much as it can. The algorithm then chooses the best found one still.

    The found relations of Falcon 2.0 are added with score 1.0 (maximum score). The found entities with 0.1. This is,
    because Falcon does not provide any scores. But if we find a relation, we consider it most important. If we find
    entities, we score them low because of the uncertainty.

    Args:
        s: The string where labels should be decoded.
        context: The string where entities and relations are linked and then linked to some uri.
        confidence: The confidence for entity- and relation-linking. Defaults to 0.1. We propose 0.1 as it finds
                    as much as it can. The algorithm then chooses the best found one still.

    Returns:
        A string with decoded labels if some were found.
    """
    excluded = ["xsd:"]

    text_to_uri = dict()
    text_to_uri = _get_uri_from_falcon(context=context, confidence=confidence, text_to_uri=text_to_uri)
    text_to_uri = _get_uri_from_dbpedia_spotlight(context=context, confidence=confidence, text_to_uri=text_to_uri)
    text_to_uri = _get_uri_from_tagme(context=context, confidence=confidence, text_to_uri=text_to_uri)

    prefixes = list(PREFIX_TO_URI.keys())
    prefixes = [elem for elem in prefixes if elem not in excluded]
    prefixes_regex = '|'.join(prefixes)
    for match in \
            re.finditer(f"\\b(({prefixes_regex})(?!{prefixes_regex})((?:.(?!\\b({prefixes_regex})))*?)):end_label", s):
        whole_match = match.group(0)
        prefix_and_label = match.group(1).strip()
        prefix = match.group(2)
        label = match.group(3).strip()
        prefix_uri = PREFIX_TO_URI[prefix]

        label_in_text_to_uri = False
        if label in text_to_uri:
            label_in_text_to_uri = True
            label_uris = text_to_uri[label]
            label_uris.sort(key=lambda elem: elem[1], reverse=True)
        prefix_and_label_in_text_to_uri = False
        if prefix_and_label in text_to_uri:
            prefix_and_label_in_text_to_uri = True
            prefix_and_label_uris = text_to_uri[prefix_and_label]
            prefix_and_label_uris.sort(key=lambda elem: elem[1], reverse=True)
        found = False
        # Choose the first one with same prefix.
        if not found and label_in_text_to_uri:
            for uri, _ in label_uris:
                if uri.startswith(prefix_uri):
                    s = re.sub(whole_match, '<' + uri + '>', s)
                    found = True
        if not found and prefix_and_label_in_text_to_uri:
            for uri, _ in prefix_and_label_uris:
                if uri.startswith(prefix_uri):
                    s = re.sub(whole_match, '<' + uri + '>', s)
                    found = True
        # If none with same prefix was found, choose the one with the highest score.
        if not found and label_in_text_to_uri:
            uri, _ = label_uris[0]
            s = re.sub(whole_match, '<' + uri + '>', s)
            found = True
        if not found and prefix_and_label_in_text_to_uri:
            uri, _ = prefix_and_label_uris[0]
            s = re.sub(whole_match, '<' + uri + '>', s)
    return s


def _get_uri_from_dbpedia_spotlight(context: str, confidence: float,
                                    text_to_uri: Union[dict[str, tuple[str, float]], None] = None) \
        -> dict[str, tuple[str, float]]:
    """Link entities in context using DBpedia-Spotlight and fill text_to_uri with it.

    Args:
        context: The text where entities are linked.
        confidence: The minimal confidence of linked entities.
        text_to_uri: A prior map of the text mapped to a tuple with the linked URI and a similarity score. If none is
                     provided, an empty dictionary is created.

    Returns:
          The prior map text_to_uri extended by the found linked entities.
    """
    if text_to_uri is None:
        text_to_uri = dict()

    response = query_dbspotlight(context, confidence=confidence)
    if "Resources" not in response:
        resources = list()
    else:
        resources = response["Resources"]
    for linked_entity in resources:
        if "@URI" in linked_entity and "@surfaceForm" in linked_entity and "@similarityScore" in linked_entity:
            text = linked_entity["@surfaceForm"]
            uri = linked_entity["@URI"]
            similarity_score = linked_entity["@similarityScore"]
            if text not in text_to_uri:
                text_to_uri[text] = list()
            text_to_uri[text].append((uri, float(similarity_score)))
    return text_to_uri


def _get_uri_from_tagme(context: str, confidence: float,
                        text_to_uri: Union[dict[str, tuple[str, float]], None] = None) \
        -> dict[str, tuple[str, float]]:
    """Link entities in context using TagMe and fill text_to_uri with it.

    Args:
        context: The text where entities are linked.
        confidence: The minimal confidence of linked entities.
        text_to_uri: A prior map of the text mapped to a tuple with the linked URI and a similarity score.

    Returns:
          The prior map text_to_uri extended by the found linked entities.
    """
    if text_to_uri is None:
        text_to_uri = dict()

    response = query_tagme(context)
    annotations = response["annotations"]
    for annotation in annotations:
        ann_id = annotation["id"]
        ann_conf = float(annotation["rho"])
        text = annotation["spot"]
        similarity_score = float(annotation["link_probability"])
        uri = None
        if ann_conf >= confidence:
            uri = get_uri_for_wiki_page_id(ann_id)
        if uri is not None:
            if text not in text_to_uri:
                text_to_uri[text] = list()
            text_to_uri[text].append((uri, float(similarity_score)))
    return text_to_uri


def _get_uri_from_falcon(context: str, confidence: float = 0.1,
                         text_to_uri: Union[dict[str, tuple[str, float]], None] = None) \
        -> dict[str, tuple[str, float]]:
    """Link relations in context using Falcon 2.0 and fill text_to_uri with it.

    The found relations of Falcon 2.0 are added with score 1.0. The found entities with 0.1. This is, because Falcon
    does not provide any scores. But if we find a relation, we consider it most important. If we find entities,
    we score them low because of the uncertainty.

    Args:
        context: The text where entities are linked.
        confidence: The score found entities get assigned.
        text_to_uri: A prior map of the text mapped to a tuple with the linked URI and a similarity score.

    Returns:
          The prior map text_to_uri extended by the found linked entities.
    """
    if text_to_uri is None:
        text_to_uri = dict()

    entity_score = confidence
    relation_score = 1

    response = query_falcon(context)
    if "entities_dbpedia" not in response or "relations_dbpedia" not in response:
        return text_to_uri
    entities = response["entities_dbpedia"]
    relations = response["relations_dbpedia"]

    # Add entities
    for entity in entities:
        if len(entity) >= 2:
            uri = entity[0]
            text = entity[1]
            if text not in text_to_uri:
                text_to_uri[text] = list()
            text_to_uri[text].append((uri, float(entity_score)))

    # Add entities
    for relation in relations:
        if len(relation) >= 2:
            uri = relation[0]
            text = relation[1]
            if text not in text_to_uri:
                text_to_uri[text] = list()
            text_to_uri[text].append((uri, float(relation_score)))

    return text_to_uri


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
