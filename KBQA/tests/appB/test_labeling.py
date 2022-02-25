"""Tests for finding labels for uris and vice versa."""
from typing import List
import unittest

from KBQA.appB.transformer_architectures.BERT_WordPiece_SPBERT.generator_utils import (
    get_label_for_uri,
)
from KBQA.appB.transformer_architectures.BERT_WordPiece_SPBERT.generator_utils import (
    get_uri_for_label,
)


class TestLabeling(unittest.TestCase):
    """Class for labeling tests."""

    def test_label_for_uri(self) -> None:
        """Test labels for uri."""
        uri_1 = "http://dbpedia.org/resource/Angela_Merkel"
        uri_2 = "http://dbpedia.org/ontology/capital"
        uri_3 = "http://dbpedia.org/resource/no_label_found"

        result_1 = get_label_for_uri(uri_1)
        expected_result_1 = "Angela Merkel"

        self.assertEqual(result_1, expected_result_1)

        result_2 = get_label_for_uri(uri_2)
        expected_result_2 = "capital"

        self.assertEqual(result_2, expected_result_2)

        result_3 = get_label_for_uri(uri_3)
        expected_result_3 = ""

        self.assertEqual(result_3, expected_result_3)

    def test_uri_for_label(self) -> None:
        """Test uri for label."""
        label_1 = "Angela Merkel"
        label_2 = "capital"
        label_3 = "should not exist"

        result_1 = get_uri_for_label(label_1)
        expected_result_1 = [
            "http://dbpedia.org/resource/Angela_Merkel",
            "http://dbpedia.org/resource/Category:Angela_Merkel",
        ]

        self.assertSetEqual(set(result_1), set(expected_result_1))

        result_2 = get_uri_for_label(label_2)
        expected_result_2 = [
            "http://dbpedia.org/ontology/capital",
            "http://dbpedia.org/property/capital",
        ]
        self.assertSetEqual(set(result_2), set(expected_result_2))

        result_3 = get_uri_for_label(label_3)
        expected_result_3: List[str] = list()

        self.assertSetEqual(set(result_3), set(expected_result_3))
