import unittest
from KBQA.appB.summarizers import GoldSummarizer
from KBQA.appB.data_generator import Question

class TestGoldSummarizer(unittest.TestCase):

    question_from_qald8 = Question("Who is the author of the interpretation of dreams?")
    answer_from_qald8 = "<http://dbpedia.org/resource/The_Interpretation_of_Dreams> <http://dbpedia.org/ontology/author> <http://dbpedia.org/resource/Sigmund_Freud>"
    question_from_qald9 = Question("Who was Tom Hanks married to?")
    answer_from_qald9 = "<http://dbpedia.org/resource/Tom_Hanks> <http://dbpedia.org/ontology/spouse> <http://dbpedia.org/resource/Rita_Wilson>"
    question_not_known = Question("What is the meaning of life?")
    answer_not_known = ""

    def test_summarize_qald8(self):
        """Test the summmarization of the gold summarizer for qald 8."""
        summarizer = GoldSummarizer("qald8", verbose=False)

        result_q8 = summarizer.summarize(self.question_from_qald8)
        result_q9 = summarizer.summarize(self.question_from_qald9)
        result_unknown = summarizer.summarize(self.question_not_known)

        self.assertListEqual(result_q8, [self.answer_from_qald8])
        self.assertListEqual(result_q9, [])
        self.assertListEqual(result_unknown, [])

    def test_summarize_qald9(self):
        """Test the summmarization of the gold summarizer for qald 9."""
        summarizer = GoldSummarizer("qald9", verbose=False)

        result_q8 = summarizer.summarize(self.question_from_qald8)
        result_q9 = summarizer.summarize(self.question_from_qald9)
        result_unknown = summarizer.summarize(self.question_not_known)

        self.assertListEqual(result_q8, [])
        self.assertListEqual(result_q9, [self.answer_from_qald9])
        self.assertListEqual(result_unknown, [])

    def test_summarize_unknown_question(self):
        """Test the summmarization of the gold summarizer if the question does not exist."""
        summarizer = GoldSummarizer("qald9", verbose=False)

        result_q8 = summarizer.summarize(self.question_from_qald8)
        result_q9 = summarizer.summarize(self.question_from_qald9)
        result_unknown = summarizer.summarize(self.question_not_known)

        self.assertListEqual(result_q8, [])
        self.assertListEqual(result_q9, [])
        self.assertListEqual(result_unknown, [])