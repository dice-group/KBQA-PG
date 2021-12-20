"""Module for generating question-triple-query(qtq) dataset from QALD dataset."""
import json
import re
from typing import Dict
from typing import Optional
from typing import Set

from get_answer import get_answer


def tokenize_query(query_body: str) -> list[str]:
    """
    Tokenizes the query body of a SPARQL query.

    URIs, string literals, SPARQL keywords and SPARQL punctuation are recognized as individual triples.

    :param query_body: The body of a SPARQL query
    :return: A list containing the tokenized query body
    """
    tokens = []
    new_token = ""
    ignore_space = True
    for i, char in enumerate(query_body):
        if char == " " and ignore_space:
            if new_token != "":
                tokens.append(new_token)
                new_token = ""
        elif char in [";", "{", "}"]:
            if new_token != "":
                tokens.append(new_token)
            tokens.append(char)
            new_token = ""
        elif char == ".":
            if query_body[i + 1] in [" ", "}"]:
                if new_token != "":
                    tokens.append(new_token)
                tokens.append(char)
                new_token = ""
        elif char == '"':
            ignore_space = not ignore_space
            new_token += char
        else:
            new_token += char
    return tokens


def construct_triple_templates(tokenized_query: list) -> tuple[list[str], list[str]]:
    """
    Construct triple templates from tokenized query.

    Triples that are part of a UNION statement are stored seperatly in union_triples

    :param tokenized_query: A list containing a tokenized SPARQL query body
    :return: ordinary triple- and union triple templates
    """
    triples = []
    union_triples = []
    leading_token = None
    in_union = False
    tokens = tokenized_query[1:-1]
    for token in tokens:
        if token == "{":
            leading_token = None
            in_union = True
        elif token == "}":
            leading_token = None
            in_union = False
        elif token == "UNION":
            continue
        elif leading_token is None or token == ";":
            leading_token = token if leading_token is None else leading_token
            if in_union:
                union_triples.append(leading_token)
            else:
                triples.append(leading_token)
        elif token == ".":
            leading_token = None
        else:
            if in_union:
                union_triples[-1] = union_triples[-1] + " " + token
            else:
                triples[-1] = triples[-1] + " " + token

    return triples, union_triples


def extract_sparql_prefixes(sparql_query: str) -> dict[str, str]:
    """
    Extract all SPARQL PREFIX statements into a dict.

    The abbreviations are the keys and the full names are the values.

    :param sparql_query: A complete SPARQL query
    :return: A dict containg the PREFIX statements of the SPARQL query
    """
    prefixes = {}
    tokens = sparql_query.split(" ")
    for i, token in enumerate(tokens):
        if token == "PREFIX":
            prefix_key = tokens[i + 1][:-1]
            prefix_val = tokens[i + 2]
            prefixes[prefix_key] = prefix_val
    return prefixes


def extract_qald_question_information(
    qald_question: dict,
) -> tuple[str, str, str, str, dict]:
    """
    Extract and preprocess information from QALD "question" for further processing.

    The natural language question in english is extracted.
    The SPARQL query is extracted and transformed to SELECT * WHERE query.
    The SPARQL query body is extracted from the SPARQL query,
    FITLER and OPTIONAL statements are removed from the body.
    THE SPARQL constraint at the end of the SPARQL query is extracted.
    THE PREFIX statements are extracted from the SPARQL query.

    :param qald_question: A dictionary containing a "question" from a QALD dataset
    :return: A tuple of the aformentioned gathered information.
    """
    nl_question = ""
    for question_lang in qald_question["question"]:
        if question_lang["language"] == "en":
            nl_question = question_lang["string"]
            break

    sparql_query = qald_question["query"]["sparql"]
    if "ASK" in qald_question["query"]["sparql"]:
        sparql_query = sparql_query.replace("ASK", "SELECT *")
    sparql_query = re.sub("SELECT (.*) WHERE", "SELECT * WHERE", sparql_query)
    left_start = sparql_query.index("{")
    right_start = sparql_query.rindex("}")
    query_body = sparql_query[left_start : right_start + 1]
    query_body = re.sub(r" FILTER(.*)\)", "", query_body)
    query_body = re.sub(" OPTIONAL", "", query_body)

    if "FILTER" in query_body or "OPTIONAL" in query_body:
        print(
            "[WARNING] FILTER or OPTIONAL in query_body, might lead to generation of bad triples: ",
            query_body,
        )

    query_constraint = sparql_query[right_start + 1 :]
    query_prefixes = extract_sparql_prefixes(sparql_query)

    return nl_question, sparql_query, query_body, query_constraint, query_prefixes


def get_query_results(
    sparql_query: str, query_constraint: str
) -> tuple[list, Optional[str], list]:
    """
    Execute SPARQL query and gather the results.

    If the results are supposed to be GROUPed, then information about the
    grouping variable and the results consistent with the constraint is gathered.

    :param sparql_query: A SPARQL query with the SELECT * WHERE pattern
    :param query_constraint: The query constraints of the SPARQL queries possibly containing GROUP
    :return: A list containing the SPARQL query results
    :return optional: the grouping variable and the results consistent with the group constraint
    """
    results = []
    grouping_var = None
    grouping_results = []
    if "GROUP" in query_constraint:
        grouping_var = re.findall(r"\?(.*?) ", query_constraint)[0]
        grouping_sparql_query = sparql_query.replace("*", "?" + grouping_var)
        right_start = sparql_query.rindex("}")

        answer = get_answer(sparql_query[: right_start + 1])
        results = list(answer["results"]["bindings"])

        grouping_answer = get_answer(grouping_sparql_query)
        grouping_results = [
            res[grouping_var]["value"] for res in grouping_answer["results"]["bindings"]
        ]
    else:
        answer = get_answer(sparql_query)
        results = list(answer["results"]["bindings"])

    return results, grouping_var, grouping_results


def build_triples(
    triple_templates: list,
    results: dict,
    check_triple: bool = False,
    ask_template: str = "",
) -> set:
    """
    Build triples from SPARQL query results.

    Optionally check the validity of constructed triples.

    :param triple_templates: Templates with variables to replaces e.g. ?uri dbo:a dbr:b
    :param results: results gathered by get_answer
    :param check_triple: Flag for enabling triple verification
    :param ask_template: SPARQL template containing all necessary prefixes e.g. PREFIX: ... ASK WHERE { * }
    :return: A set containing all relevent triples
    :raises ValueError: If SPARQL query result contains unknown data-type
    """
    triples: Set[str] = set()
    for template in triple_templates:
        new_triple = template
        for var in results.keys():
            result_string = results[var]["value"]
            result_string = result_string.replace("\n", "\\n")
            if results[var]["type"] == "uri":
                new_triple = new_triple.replace("?" + var, "<" + result_string + ">")
            elif results[var]["type"] == "literal":
                language = results[var]["xml:lang"]
                new_triple = new_triple.replace(
                    "?" + var, '"' + result_string + '"' + "@" + language
                )
            elif results[var]["type"] == "typed-literal":
                datatype = results[var]["datatype"]
                new_triple = new_triple.replace(
                    "?" + var, '"' + result_string + '"^^<' + datatype + ">"
                )
            else:
                raise ValueError(
                    f'[ERROR] Unexpected result type: {results[var]["type"]}'
                )
        # print(new_triple)
        if check_triple:
            ask_query = ask_template.replace("*TRIPLE*", new_triple)
            ask_result = get_answer(ask_query)
            if not ask_result["boolean"]:
                continue
        triples = triples | {new_triple}
    return triples


def get_relevant_triples(
    query_prefixes: dict,
    sparql_query: str,
    query_constraint: str,
    triple_templates: list,
    union_templates: list,
) -> set:
    """
    Gather all relevant triples.

    :param query_prefixes: prefixes of sparql_query
    :param sparql_query: A SPARQL query with the SELECT * WHERE pattern
    :param query_constraint: The query constraints of the SPARQL queries possibly containing GROUP
    :param triple_templates: templates for the normal triple queries
    :param union_templates: templates for the union triple queries
    :return: A set of all relevant triples
    """
    ask_template = ""
    for prefix, val in query_prefixes.items():
        ask_template += "PREFIX " + prefix + ": " + val + " "
    ask_template += "ASK WHERE { *TRIPLE* . }"
    relevant_triples = set()
    results, grouping_var, grouping_results = get_query_results(
        sparql_query, query_constraint
    )
    print(grouping_var, grouping_results)

    for result in results:
        print(result)
        if grouping_var and not result[grouping_var]["value"] in grouping_results:
            print(
                result[grouping_var]["value"],
                "is not satisfying the GROUP BY constraint",
            )
            continue
        triples = build_triples(triple_templates, result)
        union_triples = build_triples(
            union_templates, result, check_triple=True, ask_template=ask_template
        )

        if not union_templates or len(union_triples) != 0:
            relevant_triples |= triples
            relevant_triples |= union_triples
        else:
            print("Triples:", triples)
            print("Not compatible with union templates:", union_templates)
    return relevant_triples


def load_dataset(dataset_path: str) -> dict:
    """
    Load dataset from given path.

    :param dataset_path: Path to QALD dataset
    :return: The dataset in QALD format
    """
    with open(dataset_path, "r", encoding="utf-8") as file_handle:
        qald_data = json.load(file_handle)

    qald_id_pattern = r"qald-[0-9]+-(train|test)-multilingual"
    print(qald_data["dataset"]["id"])
    print(qald_id_pattern)
    if "dataset" not in qald_data or not re.match(
        qald_id_pattern, qald_data["dataset"]["id"]
    ):
        print(f"[ERROR] {dataset_path} is not a QALD dataset")
        sys.exit(1)
    return qald_data


def get_args() -> str:
    """
    Get the arguments from CLI.

    :return: file path to QALD dataset
    """
    opt_args, _ = getopt.getopt(sys.argv[1:], "f", ["dataset="])
    dataset_path = "Data/qald-9-train-multilingual.json"
    for opt, value in opt_args:
        if opt in ("-f", "--dataset"):
            dataset_path = value
    return dataset_path


def main() -> None:
    """
    Load QALD dataset, processes it and stores qtq dataset.

    Function is called iff this script is "__main__".

    Synopsis:
    python3 data_gen.py {--dataset | -f} <qald-dataset>
    """
    dataset_path = get_args()
    qald_data = load_dataset(dataset_path)
    result_dict: Dict = {"questions": []}
    for question in qald_data["questions"]:
        (
            nl_question,
            sparql_query,
            query_body,
            query_constraint,
            query_prefixes,
        ) = extract_qald_question_information(question)

        tokens = tokenize_query(query_body)
        triple_templates, union_templates = construct_triple_templates(tokens)

        relevant_triples = get_relevant_triples(
            query_prefixes,
            sparql_query,
            query_constraint,
            triple_templates,
            union_templates,
        )

        print(relevant_triples)
        qtq_dict: Dict = {}
        qtq_dict["question"] = nl_question
        qtq_dict["query"] = question["query"]["sparql"]
        qtq_dict["triples"] = list(relevant_triples)
        result_dict["questions"].append(qtq_dict)
        print("\n\n")
        # print(pattern_variables,end='\n\n')
    with open(
        dataset_path.replace("qald", "qtq"), "w", encoding="utf-8"
    ) as file_handle:
        json.dump(result_dict, file_handle, indent=4, separators=(",", ": "))


if __name__ == "__main__":
    import sys
    import getopt

    main()
