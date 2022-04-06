import unittest

from KBQA.appB.summarizers import BaseSummarizer
from KBQA.appB.summarizers import FromAnswerSummarizer
from KBQA.appB.summarizers import NES


class TestImports(unittest.TestCase):
    def test_summarizer_imports(self):
        nes = NES()
        from_answer_summarizer = FromAnswerSummarizer()
        # one_hop_rank_summarizer = OneHopRankSummarizer()

        self.assertIsInstance(nes, BaseSummarizer)
        self.assertIsInstance(from_answer_summarizer, BaseSummarizer)
        # self.assertIsInstance(one_hop_rank_summarizer, BaseSummarizer)
