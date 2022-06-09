import unittest

from KBQA.appB.summarizers import OneHopRankSummarizer
from KBQA.appB.data_generator import Question
from rdflib import Graph
from rdflib import URIRef


germany = URIRef("http://dbpedia.org/resource/Germany")
capital = URIRef("http://dbpedia.org/ontology/capital")
berlin = URIRef("http://dbpedia.org/resource/Berlin")
france = URIRef("http://dbpedia.org/France")
paris = URIRef("http://dbpedia.org/resource/Paris")
leadername = URIRef("http://dbpedia.org/ontology/leadername")
angela_merkel = URIRef("http://dbpedia.org/resource/Angela_Merkel")
olaf_scholz = URIRef("http://dbpedia.org/resource/Olaf_Scholz")

class TestOneHopRankSummarizer(unittest.TestCase):

    def test_graph_triples(self):
        """Test the _get_graph_triples function."""

        ohrs = OneHopRankSummarizer()
        entities, triples = ohrs._get_graph_triples("What is the capital of Germany?")

        self.assertEqual(len(triples), 2)

        for triple in triples:
            self.assertEqual(type(triple[0][0]), URIRef)
            self.assertEqual(type(triple[0][1]), URIRef)
            self.assertEqual(type(triple[0][2]), URIRef)
            self.assertEqual(type(triple[1]), float)
            self.assertEqual(type(triple[2]), float)

    def test_filter_triples(self):
        """Test the _filter_triples function."""

        ohrs = OneHopRankSummarizer(lower_rank=3, confidence=0.6)

        triple_1 = (germany, leadername, angela_merkel) # should be included
        triple_2 = (germany, leadername, olaf_scholz) # should not be included
        triple_3 = (germany, capital, paris) # should not be included

        test_triples = [(triple_1, 5, 0.8), (triple_2, 2, 0.9), (triple_3, 5, 0.1)]
        filtered_triples = ohrs._filter_triples(test_triples)
        expected_result = [(triple_1, 5, 0.8)]

        self.assertListEqual(filtered_triples, expected_result)

    def test_aggregate_triples(self):
        """Test the _aggregate_triples function."""

        ohrs = OneHopRankSummarizer(max_triples=1)

        triple_1 = (germany, leadername, angela_merkel)
        triple_2 = (germany, leadername, olaf_scholz)
        triple_3 = (germany, capital, berlin)

        test_triples = [(triple_1, 4, 0.8), (triple_2, 3, 0.8), (triple_3, 2, 0.6)]
        aggregated_triples = ohrs._aggregate_triples(test_triples)
        expected_result = [(triple_1, 4, 0.8), (triple_3, 2, 0.6)]

        self.assertListEqual(aggregated_triples, expected_result)


    def test_format_triples(self):
        """Test the _format_triples function."""

        ohrs = OneHopRankSummarizer()

        triple_1 = (germany, capital, berlin)
        triple_2 = (france, capital, paris)
        test_triples = [(triple_1, 5, 0.8), (triple_2, 3, 0.6)]

        formated_triples = ohrs._format_triples(test_triples)
        expected_result = [f"{germany.n3()} {capital.n3()} {berlin.n3()}", f"{france.n3()} {capital.n3()} {paris.n3()}"]

        self.assertListEqual(expected_result, formated_triples)

    def test_integration(self):
        question = Question("Which subsidiary of TUI Travel serves both Glasgow and Dublin?")
        limit = 100      

        ohrs = OneHopRankSummarizer(limit=limit)

        result = ohrs.summarize(question)
        self.assertEqual(len(result), limit)

        