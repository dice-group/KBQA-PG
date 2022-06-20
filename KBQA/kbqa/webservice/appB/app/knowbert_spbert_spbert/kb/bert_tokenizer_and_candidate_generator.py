import copy
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from allennlp.common.registrable import Registrable
from allennlp.data import Token
from allennlp.data.fields import ArrayField
from allennlp.data.fields import ListField
from allennlp.data.fields import SpanField
from allennlp.data.fields import TextField
from allennlp.data.token_indexers import SingleIdTokenIndexer
from allennlp.data.token_indexers import TokenIndexer
from allennlp.data.tokenizers import PretrainedTransformerTokenizer
from app.knowbert_spbert_spbert.kb.common import get_empty_candidates
from app.knowbert_spbert_spbert.kb.common import MentionGenerator
from app.knowbert_spbert_spbert.kb.dict_field import DictField
import numpy as np
from pytorch_pretrained_bert.tokenization import BasicTokenizer

knowbert_logger = logging.getLogger("knowbert-logger.candidate-generator")

start_token = "[CLS]"
sep_token = "[SEP]"


class TokenizerAndCandidateGenerator(Registrable):
    pass


@TokenizerAndCandidateGenerator.register("bert_tokenizer_and_candidate_generator")
class BertTokenizerAndCandidateGenerator(Registrable):
    def __init__(
        self,
        entity_candidate_generators: Dict[str, MentionGenerator],
        entity_indexers: Dict[str, TokenIndexer],
        bert_model_type: str,
        do_lower_case: bool,
        whitespace_tokenize: bool = True,
        max_word_piece_sequence_length: int = 512,
    ) -> None:
        """
        Note: the fields need to be used with a pre-generated allennlp vocabulary
        that contains the entity id namespaces and the bert name space.
        entity_indexers = {'wordnet': indexer for wordnet entities,
                          'wiki': indexer for wiki entities}
        """
        # load BertTokenizer from huggingface
        self.candidate_generators = entity_candidate_generators
        self.bert_tokenizer = PretrainedTransformerTokenizer(bert_model_type)
        self.bert_word_tokenizer = BasicTokenizer(do_lower_case=False)
        # Target length should include start and end token
        self.max_word_piece_sequence_length = max_word_piece_sequence_length

        self._entity_indexers = entity_indexers
        # for bert, we'll give an empty token indexer with empty name space
        # and do the indexing directly with the bert vocab to bypass
        # indexing in the indexer
        self._bert_single_id_indexer = {"tokens": SingleIdTokenIndexer()}
        self.do_lowercase = do_lower_case
        self.whitespace_tokenize = whitespace_tokenize
        self.dtype = np.float32

    def _word_to_word_pieces(self, word: str) -> List[Token]:
        if self.do_lowercase and word not in list(
            self.bert_tokenizer.tokenizer.special_tokens_map.values()
        ):
            word = word.lower()
        return self.bert_tokenizer.tokenize(word)[
            1:-1
        ]  # exclude [CLS] and [SEP] at beginning and end

    def tokenize_and_generate_candidates(
        self,
        text_a: str,
    ) -> Dict[str, Any]:
        """
        # run BertTokenizer.basic_tokenizer.tokenize on sentence1 and sentence2 to word tokenization
        # generate candidate mentions for each of the generators and for each of sentence1 and 2 from word tokenized text
        # run BertTokenizer.wordpiece_tokenizer on sentence1 and sentence2
        # truncate length, add [CLS] and [SEP] to word pieces
        # compute token offsets
        # combine candidate mention spans from sentence1 and sentence2 and remap to word piece indices

        returns:

        {'tokens': List[str], the word piece strings with [CLS] [SEP]
         'segment_ids': List[int] the same length as 'tokens' with 0/1 for sentence1 vs 2
         'candidates': Dict[str, Dict[str, Any]],
            {'wordnet': {'candidate_spans': List[List[int]],
                         'candidate_entities': List[List[str]],
                         'candidate_entity_prior': List[List[float]],
                         'segment_ids': List[int]},
             'wiki': ...}
        }
        """
        offsets_a, grouped_wp_a, tokens_a = self._tokenize_text(text_a)

        length_a = sum(len(x) for x in grouped_wp_a)
        while self.max_word_piece_sequence_length - 2 < length_a:
            discarded = grouped_wp_a.pop()
            length_a -= len(discarded)

        word_piece_tokens_a = [
            word_piece for word in grouped_wp_a for word_piece in word
        ]
        offsets_a = offsets_a[: len(grouped_wp_a)]
        tokens_a = tokens_a[: len(grouped_wp_a)]
        instance_a = self._generate_sentence_entity_candidates(tokens_a, offsets_a)

        # Single sentence
        tokens = [start_token] + word_piece_tokens_a + [sep_token]
        segment_ids = len(tokens) * [0]
        offsets_a = [x + 1 for x in offsets_a]

        for name in instance_a.keys():
            for span in instance_a[name]["candidate_spans"]:
                span[0] += 1
                span[1] += 1

        fields: Dict[str, Any] = {}
        candidates = instance_a

        for entity_type in candidates.keys():
            # deal with @@PADDING@@
            if len(candidates[entity_type]["candidate_entities"]) == 0:
                candidates[entity_type] = get_empty_candidates()
            else:
                padding_indices = []
                has_entity = False
                for cand_i, candidate_list in enumerate(
                    candidates[entity_type]["candidate_entities"]
                ):
                    if candidate_list == ["@@PADDING@@"]:
                        padding_indices.append(cand_i)
                        candidates[entity_type]["candidate_spans"][cand_i] = [-1, -1]
                    else:
                        has_entity = True
                indices_to_remove = []
                if has_entity and len(padding_indices) > 0:
                    # remove all the padding entities since have some valid
                    indices_to_remove = padding_indices
                elif len(padding_indices) > 0:
                    assert len(padding_indices) == len(
                        candidates[entity_type]["candidate_entities"]
                    )
                    indices_to_remove = padding_indices[1:]
                for ind in reversed(indices_to_remove):
                    del candidates[entity_type]["candidate_spans"][ind]
                    del candidates[entity_type]["candidate_entities"][ind]
                    del candidates[entity_type]["candidate_entity_priors"][ind]

        # get the segment ids for the spans
        for key, cands in candidates.items():
            span_segment_ids = []
            for candidate_span in cands["candidate_spans"]:
                span_segment_ids.append(segment_ids[candidate_span[0]])
            candidates[key]["candidate_segment_ids"] = span_segment_ids

        fields["tokens"] = tokens
        fields["segment_ids"] = segment_ids
        fields["candidates"] = candidates
        fields["offsets_a"] = offsets_a
        return fields

    def _tokenize_text(self, text: str) -> Tuple[List[int], List[List[str]], List[str]]:
        if self.whitespace_tokenize:
            tokens = text.split()
        else:
            tokens = self.bert_word_tokenizer.tokenize(text)

        word_piece_tokens = []
        offsets = [0]
        for token in tokens:
            word_pieces = self._word_to_word_pieces(token)
            offsets.append(offsets[-1] + len(word_pieces))
            word_piece_tokens.append([word_piece.text for word_piece in word_pieces])
        del offsets[0]

        knowbert_logger.debug(f"offsets: {offsets}")
        knowbert_logger.debug(f"word_piece_tokens: {word_piece_tokens}")
        knowbert_logger.debug(f"tokens: {tokens}")

        return offsets, word_piece_tokens, tokens

    def _generate_sentence_entity_candidates(
        self, tokens: List[str], offsets: List[int]
    ) -> Dict[str, Any]:
        """
        Tokenize sentence, trim it to the target length, and generate entity candidates.
        :param sentence
        :param target_length: The length of the output sentence in terms of word pieces.
        :return: Dict[str, Dict[str, Any]],
            {'wordnet': {'candidate_spans': List[List[int]],
                         'candidate_entities': List[List[str]],
                         'candidate_entity_priors': List[List[float]]},
             'wiki': ...}

        """
        assert len(tokens) == len(
            offsets
        ), f"Length of tokens {len(tokens)} must equal that of offsets {len(offsets)}."
        entity_instances = {}
        for name, mention_generator in self.candidate_generators.items():
            entity_instances[name] = mention_generator.get_mentions_raw_text(
                " ".join(tokens), whitespace_tokenize=True
            )

        for name, entities in entity_instances.items():
            candidate_spans = entities["candidate_spans"]
            adjusted_spans = []
            for start, end in candidate_spans:
                if 0 < start:
                    adjusted_span = [offsets[start - 1], offsets[end] - 1]
                else:
                    adjusted_span = [0, offsets[end] - 1]
                adjusted_spans.append(adjusted_span)
            entities["candidate_spans"] = adjusted_spans
            entity_instances[name] = entities
        return entity_instances

    def convert_tokens_candidates_to_fields(
        self, tokens_and_candidates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        tokens_and_candidates is the return from a previous call to
        generate_sentence_entity_candidates.  Converts the dict to
        a dict of fields usable with allennlp.
        """
        fields = {}

        fields["tokens"] = TextField(
            [Token(t) for t in tokens_and_candidates["tokens"]],
            token_indexers=self._bert_single_id_indexer,
        )

        fields["segment_ids"] = ArrayField(
            np.array(tokens_and_candidates["segment_ids"]), dtype=np.int
        )

        all_candidates = {}
        for key, entity_candidates in tokens_and_candidates["candidates"].items():
            # pad the prior to create the array field
            # make a copy to avoid modifying the input
            candidate_entity_prior = copy.deepcopy(
                entity_candidates["candidate_entity_priors"]
            )
            max_cands = max(len(p) for p in candidate_entity_prior)
            for p in candidate_entity_prior:
                if len(p) < max_cands:
                    p.extend([0.0] * (max_cands - len(p)))
            np_prior = np.array(candidate_entity_prior)
            candidate_fields = {
                "candidate_entity_priors": ArrayField(np_prior, dtype=self.dtype),
                "candidate_entities": TextField(
                    [
                        Token(" ".join(candidate_list))
                        for candidate_list in entity_candidates["candidate_entities"]
                    ],
                    token_indexers={"ids": self._entity_indexers[key]},
                ),
                "candidate_spans": ListField(
                    [
                        SpanField(span[0], span[1], fields["tokens"])
                        for span in entity_candidates["candidate_spans"]
                    ]
                ),
                "candidate_segment_ids": ArrayField(
                    np.array(entity_candidates["candidate_segment_ids"]), dtype=np.int
                ),
            }
            all_candidates[key] = DictField(candidate_fields)

        fields["candidates"] = DictField(all_candidates)

        return fields
