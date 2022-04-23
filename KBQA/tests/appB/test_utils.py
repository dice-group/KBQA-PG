import unittest

from KBQA.appB.summarizers.utils import query_dbspotlight
from KBQA.appB.summarizers.utils import entity_recognition_dbspotlight
from KBQA.appB.summarizers.utils import entity_recognition_dbspotlight_confidence
from KBQA.appB.summarizers.utils import query_tagme
from KBQA.appB.summarizers.utils import entity_recognition_tagme
from rdflib import URIRef

class TestUtils(unittest.TestCase):

    def test_query_dbspotlight(self):
        """Test the function query_dbspotlight."""

        question = "What is the capital of Germany?"

        result = query_dbspotlight(question)

        self.assertEqual(type(result), dict)
        self.assertEqual(result["@text"], question)
        self.assertTrue("Resources" in result)

    def test_entity_recognition_dbspotlight(self):
        """Test the function entity_recognition_dbspotlight."""

        question_1 = "What is the capital of Germany?"
        question_2 = "Who is the spouse of Barack Obama?"

        result_1 = entity_recognition_dbspotlight(question_1)
        result_2 = entity_recognition_dbspotlight(question_2)

        expected_result_1 = [URIRef("http://dbpedia.org/resource/Germany")]
        expected_result_2 = [URIRef("http://dbpedia.org/resource/Barack_Obama")]

        self.assertListEqual(result_1, expected_result_1)
        self.assertListEqual(result_2, expected_result_2)

    def test_entity_recognition_dbspotlight_confidence(self):
        """Test the function entity_recognition_dbspotlight_confidence."""

        question = "Who is the spouse of Barack Obama?"

        result = entity_recognition_dbspotlight_confidence(question)

        expected_entity = URIRef("http://dbpedia.org/resource/Barack_Obama")

        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0][0], expected_entity)
        self.assertEqual(type(result[0][1]), float)

    def test_query_tagme(self):
        """Test the function query_tagme."""

        question = "Who is the spouse of Barack Obama?"

        result = query_tagme(question)
        
        self.assertEqual(type(result), dict)
        self.assertTrue("annotations" in result)
        self.assertTrue(len(result["annotations"]) > 0)

    def test_entity_recognition_tagme(self):
        """Test the function entity_recognition_tagme."""

        question = "Who is the spouse of Barack Obama?"

        result = entity_recognition_tagme(question)

        expected_entity = URIRef("http://dbpedia.org/resource/Barack_Obama")

        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0][0], expected_entity)
        self.assertEqual(type(result[0][1]), float)