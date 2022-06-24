import unittest

from KBQA.appB.summarizers import LaurenSummarizer
from KBQA.appB.data_generator import Question

class TestLaurenSummarizer(unittest.TestCase):

    def test_format(self):
        """Test the format of the LaurenSummarizer."""
        question = Question("What is the alma mater of Angela Merkel?")
        lauren = LaurenSummarizer()

        result = lauren.summarize(question)

        for triple in result:
            self.assertRegex(triple, r'^<.*> <.*> <.*>')
