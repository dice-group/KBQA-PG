from summarizer import Summarizer


class NES(Summarizer):
    def summarize(self, question: str):
        return nes_ner_hop(question)
