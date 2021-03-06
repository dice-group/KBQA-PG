"""Module for generating question-triple-query(qtq) dataset from dataset."""
import re
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from KBQA.appB.data_generator import Question
from KBQA.appB.summarizers import BaseSummarizer
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper


class FromAnswerSummarizer(BaseSummarizer):
    """Summarizer which generates triples from a given SPARQL translation of a NL Question."""

    def summarize(self, question: Question) -> List[str]:
        """Summarize a natural question and return relevant triples.

        Parameters
        ----------
        question : Question
            A question object already containing a correct SPARQL translation for the NL question.

        Returns
        -------
        list[str]
            A list of triples found by the summarizer in the format "<s> <p> <o>"
        """
        (
            sparql_query,
            query_body,
            query_constraint,
            query_prefixes,
        ) = self._extract_sparql_query_metadata(question.sparql)

        tokens = self._tokenize_query(query_body)
        triple_templates, union_templates = self._construct_triple_templates(tokens)
        triple_templates = self._expand_templates(triple_templates, query_prefixes)
        union_templates = self._expand_templates(union_templates, query_prefixes)
        relevant_triples = self._get_relevant_triples(
            query_prefixes,
            sparql_query,
            query_constraint,
            triple_templates,
            union_templates,
        )

        if len(relevant_triples) == 0:
            print("No triples found:")
            print(f"question: {question.text}")
            print(f"SPARQL query: {question.sparql}")
            print(f"templates: {triple_templates}")
            print(f"union templates: {union_templates}")
            print("\n")
        return relevant_triples

    def _tokenize_query(self, query_body: str) -> List[str]:
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
                else:
                    new_token += char
            elif char == '"':
                ignore_space = not ignore_space
                new_token += char
            else:
                new_token += char
        return tokens

    def _construct_triple_templates(
        self, tokenized_query: list
    ) -> Tuple[List[str], List[str]]:
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

    def _expand_templates(self, templates: list, prefixes: dict) -> List[str]:
        """
        Expand prefixes in triples.

        :param templates: templates for triples generated by construct_triple_templates
        :param prefixes: key-value pairs for all prefixes of SPARQL query, e.g. "dbo":"<http://.../>"
        :return: list of expanded triples
        """
        expanded_templates = []
        for template in templates:
            tokens = template.split(" ")
            expanded_tokens = []
            for token in tokens:
                for prefix in prefixes:
                    if token.startswith(prefix):
                        token_value = token.replace(prefix + ":", "")
                        expanded_tokens.append(
                            "<" + prefixes[prefix][1:-1] + token_value + ">"
                        )
                        break
                else:
                    expanded_tokens.append(token)
            expanded_templates.append(" ".join(expanded_tokens))
        return expanded_templates

    def _extract_sparql_prefixes(self, sparql_query: str) -> Dict[str, str]:
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

    def _extract_sparql_query_metadata(
        self,
        sparql_query: str,
    ) -> Tuple[str, str, str, dict]:
        """
        Extract and preprocess metadata from SPARQL query for further processing.

        The SPARQL query is transformed to SELECT * WHERE query.
        The SPARQL query body is extracted from the SPARQL query,
        FITLER and OPTIONAL statements are removed from the body.
        THE SPARQL constraint at the end of the SPARQL query is extracted.
        THE PREFIX statements are extracted from the SPARQL query.

        :param sparql_query: A SPARQL query
        :return: A tuple of the aformentioned gathered information.
        """
        if "ASK" in sparql_query:
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
        query_prefixes = self._extract_sparql_prefixes(sparql_query)

        return sparql_query, query_body, query_constraint, query_prefixes

    def _execute_sparql_query(self, query: str) -> Dict:
        """
        Get results from a "SELECT WHERE" SPARQL query.

        :param query: The SPARQL query
        :return: Results for the SPARQL query
        """
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)

        answers = sparql.query().convert()
        return answers

    def _get_query_results(
        self, sparql_query: str, query_constraint: str
    ) -> Tuple[List, Optional[str], List]:
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

            answer = self._execute_sparql_query(sparql_query[: right_start + 1])
            results = list(answer["results"]["bindings"])

            grouping_answer = self._execute_sparql_query(grouping_sparql_query)
            grouping_results = [
                res[grouping_var]["value"]
                for res in grouping_answer["results"]["bindings"]
            ]
        else:
            answer = self._execute_sparql_query(sparql_query)
            results = list(answer["results"]["bindings"])

        return results, grouping_var, grouping_results

    def _build_triples(
        self,
        triple_templates: list,
        results: dict,
        check_triple: bool = False,
        ask_template: str = "",
    ) -> Set:
        """
        Build triples from SPARQL query results.

        Optionally check the validity of constructed triples.

        :param triple_templates: Templates with variables to replaces e.g. ?uri dbo:a dbr:b
        :param results: results gathered by execute_sparql_query
        :param check_triple: Flag for enabling triple verification
        :param ask_template: SPARQL template containing all necessary prefixes e.g. PREFIX: ... ASK WHERE { * }
        :return: A set containing all relevent triples
        :raises ValueError: If SPARQL query result contains unknown data-type
        """
        triples: Set[str] = set()
        for template in triple_templates:
            if len(template.split(" ")) != 3:
                continue
            new_triple = template
            for var in results.keys():
                result_string = results[var]["value"]
                result_string = result_string.replace("\n", "\\n")
                if results[var]["type"] == "uri":
                    new_triple = new_triple.replace(
                        "?" + var, "<" + result_string + ">"
                    )
                elif results[var]["type"] == "literal":
                    if "xml:lang" in results[var]:
                        language = results[var]["xml:lang"]
                        new_triple = new_triple.replace(
                            "?" + var, '"' + result_string + '"' + "@" + language
                        )
                    else:
                        new_triple = new_triple.replace(
                            "?" + var, '"' + result_string + '"'
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
                ask_result = self._execute_sparql_query(ask_query)
                if not ask_result["boolean"]:
                    continue
            triples = triples | {new_triple}
        return triples

    def _get_relevant_triples(
        self,
        query_prefixes: dict,
        sparql_query: str,
        query_constraint: str,
        triple_templates: list,
        union_templates: list,
    ) -> List:
        """
        Gather all relevant triples.

        :param query_prefixes: prefixes of sparql_query
        :param sparql_query: A SPARQL query with the SELECT * WHERE pattern
        :param query_constraint: The query constraints of the SPARQL queries possibly containing GROUP
        :param triple_templates: templates for the normal triple queries
        :param union_templates: templates for the union triple queries
        :return: A set of all relevant triples
        """
        ask_template = self._prepare_ask_template(query_prefixes)
        relevant_triples = set()
        results, grouping_var, grouping_results = self._get_query_results(
            sparql_query, query_constraint
        )

        for result in results:
            if grouping_var and not result[grouping_var]["value"] in grouping_results:
                print(
                    result[grouping_var]["value"],
                    "is not satisfying the GROUP BY constraint",
                )
                continue
            triples = self._build_triples(triple_templates, result)
            union_triples = self._build_triples(
                union_templates, result, check_triple=True, ask_template=ask_template
            )

            if not union_templates or len(union_triples) != 0:
                relevant_triples |= triples
                relevant_triples |= union_triples
            else:
                print("Triples:", triples)
                print("Not compatible with union templates:", union_templates)
        return list(relevant_triples)

    def _prepare_ask_template(self, query_prefixes: dict) -> str:
        """Prepare ask template for given prefixes.

        :param query_prefixes: prefixes of sparql_query
        :return: template for a single triple ASK question
        """
        ask_template = ""
        for prefix, val in query_prefixes.items():
            ask_template += "PREFIX " + prefix + ": " + val + " "
        ask_template += "ASK WHERE { *TRIPLE* . }"
        return ask_template
