from pyparsing import Word
import spacy
from KBQA.appB.transformer_architectures.kb.common import WhitespaceTokenizer
from typing import List
from allennlp.data import Token

class WordNetSpacyPreprocessor:
    """
    A "preprocessor" that really does POS tagging and lemmatization using spacy,
    plus some hand crafted rules.

    allennlp tokenizers take strings and return lists of Token classes.
    we'll run spacy first, then modify the POS / lemmas as needed, then
    return a new list of Token
    """
    def __init__(self, whitespace_tokenize_only: bool = False):
        self.nlp = spacy.load('en_core_web_sm', disable=[ 'parser', 'ner', 'textcat'])
        if whitespace_tokenize_only:
            self.nlp.tokenizer = WhitespaceTokenizer(self.nlp.vocab)

        # spacy POS are similar, but not exactly the same as wordnet,
        # so need this conversion for tags that need to be mapped
        self.spacy_to_wordnet_map = {
            'PROPN': 'NOUN'
        }

    def __call__(self, text: str) -> List[Token]:
        spacy_doc = self.nlp(text)
        for spacy_token in spacy_doc:
            print(spacy_token.text)
            print(spacy_token.lemma_)
            print(type(spacy_token.pos_))
            print(spacy_token.pos_)
        # create allennlp tokens
        normalized_tokens = [
            Token(
                spacy_token.text,
                pos_=self.spacy_to_wordnet_map.get(spacy_token.pos_, spacy_token.pos_),
                lemma_=spacy_token.lemma_
            )

            for spacy_token in spacy_doc
            if not spacy_token.is_space
        ]

        return normalized_tokens

sentence = "Paris is located in France."

spacy_prep = WordNetSpacyPreprocessor(whitespace_tokenize_only=False)
spacy_prep_white = WordNetSpacyPreprocessor(whitespace_tokenize_only=True)

spacy_doc = spacy_prep(sentence)
spacy_doc = spacy_prep_white(sentence)
