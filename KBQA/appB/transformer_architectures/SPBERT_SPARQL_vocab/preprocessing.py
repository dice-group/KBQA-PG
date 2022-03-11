"""Preprocess data."""
import json
import os
import re
import traceback
from tqdm import tqdm

from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper import JSON
from pathlib import Path

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
    "vrank:": "http://purl.org/voc/vrank#",
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
    ["http://www.opengis.net/ont/geosparql#", "https://www.opengis.net/ont/geosparql#", "geo:"],
    ["http://www.opengis.net/def/function/geosparql/", "https://www.opengis.net/def/function/geosparql/", "geof:"],
    ["http://purl.org/voc/vrank#", "https://purl.org/voc/vrank#", "vrank:"],
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
    [". ", " .", " . ", " . "],  # Normalize as much as possible without tearing apart decimals
    [", ", " ,", " , ", " , "],  # TODO: Check if this really is valid all the time
    ["; ", " ;", " ; ", " ; "],
]
ENCODING_REPLACEMENTS = [
    ['?', " variable: ", " ?"],
    ["*", " all variables ", " * "],
    ["<=", " less equal ", " <= "],
    [">=", " greater equal ", " >= "],
    ["!=", " not equal ", " != "],
    ["=", " equal ", " = "],  # After <=, >=, !=
    ["<", " less than ", " < "],  # After <=, >= and after getting rid of chevrons
    [">", " greater than ", " > "],  # After <=, >= and after getting rid of chevrons
    ["||", " logical or ", " || "],
    ["&&", " logical and ", " && "],
    ["!", " logical not ", " ! "],  # After !=
    ["@en", " language English ", "@en"],  # For now, we are only considering english literals
]


def preprocess_qtq_file(file_name, input_file_path, output_file_path="preprocessed_data_files",
                        keep_separated_input_file=False):
    """Separate and preprocess a JSON qtq-file into three files, question-, triple-, sparql-file.

    Let file_name_without_json be the file_name without the trailing ".json".
    Store the preprocessed questions in <output_file_path>/<file_name_without_json>.en.
    Store the preprocessed triples in <output_file_path>/<file_name without_json>.triple.
    Store the preprocessed SPARQL queries in <output_file_path>/<file_name_without_json>.sparql.

    Also applies filter_triples() on the triples of the qtq-file.

    Args:
        file_name: The name of the input qtq-file. Must be encoded as JSON and the name must end in ".json".
        keep_separated_input_file: If True, store the separated qtq-file in <output_file_path>/separated_input_files/.
    """
    if not file_name.endswith(".json"):
        raise ValueError("file_name should be ending with \".json\"")
    file_name = file_name.removesuffix(".json")
    input_file_path = input_file_path.rstrip("/")
    output_file_path = output_file_path.rstrip("/")
    Path(output_file_path).mkdir(parents=True, exist_ok=True)
    separated_input_file_path = output_file_path + "/separated_input_files"
    separate_qtq_file(file_name=file_name + ".json", input_file_path=input_file_path,
                      output_file_path=separated_input_file_path)
    preprocess_natural_language_file(file_name=file_name + ".en", input_file_path=separated_input_file_path,
                                     output_file_path=output_file_path)
    preprocess_sparql_file(file_name=file_name + ".sparql", input_file_path=separated_input_file_path,
                           output_file_path=output_file_path)
    preprocess_triples_file(file_name=file_name + ".triple", input_file_path=separated_input_file_path,
                            output_file_path=output_file_path)
    separated_input_file_path = separated_input_file_path.rstrip('/')
    if not keep_separated_input_file:
        os.remove(separated_input_file_path + '/' + file_name + ".en")
        os.remove(separated_input_file_path + '/' + file_name + ".triple")
        os.remove(separated_input_file_path + '/' + file_name + ".sparql")
        if not any(os.scandir(separated_input_file_path)):
            os.rmdir(separated_input_file_path)


def filter_triples(triples: list) -> list:
    """
    Filter out triples containing \\n character.

    :param triples: list of triples
    :return: list of filtered triples
    """
    return [triple for triple in triples if "\n" not in triple]


def separate_qtq_file(file_name, input_file_path, output_file_path="preprocessed_data_files/separated_input_files"):
    """Separate a JSON qtq-file into three files, question-, triple-, sparql-file.

    Let file_name_without_json be the file_name without the trailing ".json".
    Store the questions in <output_file_path>/<file_name_without_json>.en.
    Store the triples in <output_file_path>/<file_name without_json>.triple.
    Store the SPARQL queries in <output_file_path>/<file_name_without_json>.sparql.

    Also applies filter_triples() on the triples of the qtq-file.

    Args:
        file_name: The name of the input qtq-file. Must be encoded as JSON and the name must end in ".json".
    """
    if not file_name.endswith(".json"):
        raise ValueError("file_name should be ending with \".json\"")
    file_name = file_name.removesuffix(".json")
    input_file_path = input_file_path.rstrip("/")
    output_file_path = output_file_path.rstrip("/")
    Path(output_file_path).mkdir(parents=True, exist_ok=True)
    en_file = open(f"{output_file_path}/{file_name}.en", "w")
    sparql_file = open(f"{output_file_path}/{file_name}.sparql", "w")
    triple_file = open(f"{output_file_path}/{file_name}.triple", "w")
    data = json.load(open(f"{input_file_path}/{file_name}.json", "r"))
    for element in data["questions"]:
        en_file.write(element["question"] + "\n")
        sparql_file.write(element["query"] + "\n")
        triple_file.write("\t".join(filter_triples(element["triples"])) + "\n")

    en_file.close()
    sparql_file.close()
    triple_file.close()


def preprocess_natural_language_file(file_name, input_file_path, output_file_path="preprocessed_data_files"):
    input_file_path = input_file_path.rstrip("/")
    output_file_path = output_file_path.rstrip("/")
    Path(output_file_path).mkdir(parents=True, exist_ok=True)
    with open(f"{output_file_path}/{file_name}", 'w') as out:
        with open(f"{input_file_path}/{file_name}", 'r') as f:
            for line in tqdm(f, desc="Amount of preprocessed questions", unit=" questions"):
                if "\n" == line[-1]:
                    line = line[:-1]
                out.write(preprocess_natural_language_sentence(line))
                out.write("\n")


def preprocess_natural_language_sentence(w):
    # creating a space between a word and the punctuation following it
    # eg: "he is a boy." => "he is a boy ."
    # Reference:-
    #   https://stackoverflow.com/questions/3645931/python-padding-punctuation-with-white-spaces-keeping-punctuation
    w = re.sub(r"([?.!,¿])", r" \1 ", w)
    w = re.sub(r'[" "]+', " ", w)

    # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
    # w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)
    # w = re.sub(r'\[.*?\]', '<ans>', w).rstrip().strip()
    w = w.rstrip().strip().lower()

    # adding a start and an end token to the sentence
    # so that the model know when to start and stop predicting.
    # w = '<start> ' + w + ' <end>'
    return w


def preprocess_sparql_file(file_name, input_file_path, output_file_path="preprocessed_data_files"):
    # TODO: Store checkpoints.
    input_file_path = input_file_path.rstrip("/")
    output_file_path = output_file_path.rstrip("/")
    Path(output_file_path).mkdir(parents=True, exist_ok=True)
    with open(f"{output_file_path}/{file_name}", 'w') as out:
        with open(f"{input_file_path}/{file_name}", 'r') as f:
            for line in tqdm(f, desc="Amount of preprocessed SPARQL examples", unit=" examples"):
                if "\n" == line[-1]:
                    line = line[:-1]
                out.write(preprocess_sparql(line))
                out.write("\n")


def preprocess_sparql(s):
    # Substitute prefix by URI
    for pre_name, pre_url in re.findall(r"PREFIX\s([^:]*):\s<([^>]+)>", s):
        s = re.sub(f"\\b{pre_name}:([^\\s]+)", f"<{pre_url}\\1>", s)
    # Remove prefixes
    s = re.sub(r"PREFIX\s[^\s]*\s[^\s]*", "", s)

    # replace single quote to double quote
    s = re.sub(r"(\B')", '"', s)
    s = re.sub(r"'([^_A-Za-z])", r'"\1', s)

    # remove timezone 0
    s = re.sub(r"(\d{4}-\d{2}-\d{2})T00:00:00Z", r"\1", s)

    s = sparql_keyword_to_lower_case(s)
    s = uri_to_prefix(s)
    s = re.sub(r"@en", r"@en", s, flags=re.IGNORECASE)  # Normalize only English language tag for now.
    s = do_replacements(s, VALID_SPARQL_REPLACEMENTS)
    s = encode(s)
    return s.strip()


def preprocess_triples_file(file_name, input_file_path, output_file_path="preprocessed_data_files"):
    input_file_path = input_file_path.rstrip("/")
    output_file_path = output_file_path.rstrip("/")
    Path(output_file_path).mkdir(parents=True, exist_ok=True)
    with open(f"{output_file_path}/{file_name}", 'w') as out:
        with open(f"{input_file_path}/{file_name}", 'r') as f:
            for line in tqdm(f, desc="Amount of preprocessed triple-sets", unit=" triple-sets"):
                if "\n" == line[-1]:
                    line = line[:-1]
                triples = line.split("\t")
                out.write("\t".join(preprocess_triples(triples)))
                out.write("\n")


def preprocess_triples(triples):
    return [preprocess_sparql(triple) for triple in triples]


def encode(sparql):
    """Encode sparql.

    sparql will not be a valid SPARQL query afterwards and has to be decoded by decode() first.
    """
    s = sparql
    s = do_replacements(s, ENCODING_REPLACEMENTS)
    s = encode_datatype(s)  # TODO: Can we get rid of xsd:? Test if xsd: is the datatype always.
    # s = encode_prefix_uri(s)  # TODO: Make this accessible.
    # TODO: Replace prefixes by natural language
    return s


def decode(encoded_sparql):
    """"Decode encoded sparql to make it a valid sparql query again."""
    s = encoded_sparql
    # s = decode_prefix_uri(s)
    s = decode_datatype(s)
    s = revert_replacements(s, ENCODING_REPLACEMENTS)
    # TODO: Inline prefixes
    return s


def decode_file(file):
    """Decodes a file of encoded SPARQLs."""
    # TODO:


def uri_to_prefix(s):
    """Substitute the default SPARQL URIs with their prefixes.

    PREFIX_SUBSTITUTION defines the substitutions to be done. For one row, all column entries are substituted by the
    last column entry.

    Args:
        s: string where the substitution is made.
    """
    # TODO: Can we do this in one regex?
    # Substitute prefixes
    for r in PREFIX_SUBSTITUTION:
        encoding = r[-1]
        for original in r[:-1]:
            s = s.replace(original, encoding)
    # Get rid of chevrons
    for list_ in PREFIX_SUBSTITUTION:
        prefix = list_[-1]
        s = re.sub(f"<({prefix}[^>]+)>", r"\1", s)
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
        s = ' '.join(s.split())
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
        s = ' '.join(s.split())
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


def encode_prefix_uri(s):
    """Replace "<prefix:><path>" by "<prefix:> <label_of_the_corresponding_URI> :end_label".

    ":end_label" should be part of the tokenizer vocabulary.
    Excluded prefixes are: "xsd:".
    """
    # TODO: Test encoding -> decoding performance for labels overall.
    # TODO: Check within the preprocessed file if the found labels are reasonable.
    prefixes = ["dbo:", "dbp:", "dbc:", "dbr:", "rdf:", "rdfs", "dct:", "dc:", "georss:", "geo:", "geof:",
                "vrank:", "bif:", "foaf:", "owl:", "yago:", "skos:"]
    for prefix in prefixes:
        s = re.sub(f"(\\b{prefix})(([^\\s.,;]|(\\.[^\\s,;]))+)", generate_encoded_prefix_uri, s)
    s = ' '.join(s.split())
    return s


def generate_encoded_prefix_uri(match):
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
    except Exception:
        traceback.print_exc()
        print(f"The corresponding query is:\n{query}")
    else:
        results = answer["results"]["bindings"]
        if len(results) > 0:
            label = results[0]["label"]["value"]

    if label is None:
        return prefix + path
    return prefix + ' ' + label + " :end_label "


def decode_prefix_uri(s):
    """Replace "<prefix:> <label_of_the_corresponding_URI> :end_label" by "<prefix:><path>".

    ":end_label" should be part of the tokenizer vocabulary.
    """
    # TODO: Test decoding for many examples.
    prefixes = ["dbo:", "dbp:", "dbc:", "dbr:", "rdf:", "rdfs", "xsd:", "dct:", "dc:", "georss:", "geo:", "geof:",
                "vrank:", "bif:", "foaf:", "owl:", "yago:", "skos:"]
    prefixes_regex = '|'.join(prefixes)
    s = re.sub(f"\\b({prefixes_regex})((?!{prefixes_regex})|(.(?!{prefixes_regex}))*?):end_label",
               generate_decoded_prefix_uri, s)
    return s


def generate_decoded_prefix_uri(match):
    """Generates the string for "<prefix:> <label_of_the_corresponding_URI> :end_label" which is "<prefix:><path>".

    Only supports english labels, i.e. "<label>"@en.

    Args:
        match: A re.Match object.
    Returns:
        string: Some "<prefix:><path>" if a uri is found. Else an empty string "".
    """
    print(match.group(0))
    print(match.group(1))
    print(match.group(2))
    prefix = match.group(1)
    label = match.group(2).strip()
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
    except Exception:
        traceback.print_exc()
        print(f"The corresponding query is:\n{query}")
    else:
        bindings = response["results"]["bindings"]
        if len(bindings) > 0:
            uri = bindings[0]["uri"]["value"]

    if uri is None:
        return ""
    prefix_uri = uri_to_prefix(uri)
    return prefix_uri
