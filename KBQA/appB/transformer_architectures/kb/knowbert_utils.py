import logging
from typing import List
from typing import Union

from allennlp.common import Params
from allennlp.common.file_utils import cached_path
from allennlp.data import Batch
from allennlp.data import Instance
from allennlp.data import Vocabulary
from KBQA.appB.transformer_architectures.kb.bert_tokenizer_and_candidate_generator import BertTokenizerAndCandidateGenerator
from KBQA.appB.transformer_architectures.kb.entity_linking import TokenCharactersIndexerTokenizer
from KBQA.appB.transformer_architectures.kb.wiki_linking_util import WikiCandidateMentionGenerator
from KBQA.appB.transformer_architectures.kb.wordnet import WordNetCandidateMentionGenerator
import torch

knowbert_logger = logging.getLogger("knowbert-logger.batchifier")


def replace_candidates_with_mask_entity(candidates, spans_to_mask):
    """
    candidates = key -> {'candidate_spans': ...}
    """
    for candidate_key in candidates.keys():
        indices_to_mask = []
        for k, candidate_span in enumerate(
            candidates[candidate_key]["candidate_spans"]
        ):
            if tuple(candidate_span) in spans_to_mask:
                indices_to_mask.append(k)
        for ind in indices_to_mask:
            candidates[candidate_key]["candidate_entities"][ind] = ["@@MASK@@"]
            candidates[candidate_key]["candidate_entity_priors"][ind] = [1.0]


def _extract_config_from_archive(model_archive):
    import tarfile
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(model_archive, "r:gz") as archive:
            archive.extract("config.json", path=tmp)
            config = Params.from_file(os.path.join(tmp, "config.json"))
    return config


def _find_key(d, key):
    val = None
    stack = [d.items()]
    while len(stack) > 0 and val is None:
        s = stack.pop()
        for k, v in s:
            if k == key:
                val = v
                break
            elif isinstance(v, dict):
                stack.append(v.items())
    return val


def build_tokenizer_and_candidate_generator():
    knowbert_logger.info("Building Generators")
    wiki_tokenizer_params = {
        "namespace": "entity_wiki",
        "tokenizer": {"type": "just_spaces"},
    }
    wiki_tokenizer = TokenCharactersIndexerTokenizer.from_params(
        Params(wiki_tokenizer_params)
    )

    wordnet_tokenizer_params = {
        "namespace": "entity_wordnet",
        "tokenizer": {"type": "just_spaces"},
    }
    wordnet_tokenizer = TokenCharactersIndexerTokenizer.from_params(
        Params(wordnet_tokenizer_params)
    )

    entity_indexers = {"wiki": wiki_tokenizer, "wordnet": wordnet_tokenizer}
    knowbert_logger.info("Building Generators")
    entity_candidate_generators = {
        "wiki": WikiCandidateMentionGenerator(),
        "wordnet": WordNetCandidateMentionGenerator(
            entity_file="https://allennlp.s3-us-west-2.amazonaws.com/knowbert/wordnet/entities.jsonl"
        ),
    }
    # entity_candidate_generators = {}
    # entity_indexers = {}
    knowbert_logger.info("Build Generators")

    return BertTokenizerAndCandidateGenerator(
        entity_candidate_generators=entity_candidate_generators,
        entity_indexers=entity_indexers,
        bert_model_type="bert-base-uncased",
        do_lower_case=True,
    )


class KnowBertBatchifier:
    """
    Takes a list of sentence strings and returns a tensor dict usable with
    a KnowBert model
    """

    def __init__(
        self,
        model_archive,
        batch_size=32,
        masking_strategy=None,
        wordnet_entity_file=None,
        vocab_dir=None,
    ):

        # get bert_tokenizer_and_candidate_generator
        config = _extract_config_from_archive(cached_path(model_archive))

        # look for the bert_tokenizers and candidate_generator
        candidate_generator_params = _find_key(
            config["dataset_reader"].as_dict(), "tokenizer_and_candidate_generator"
        )

        if wordnet_entity_file is not None:
            candidate_generator_params["entity_candidate_generators"]["wordnet"][
                "entity_file"
            ] = wordnet_entity_file
        candidate_generator_params["entity_indexers"]["wiki"]["tokenizer"] = {
            "type": "just_spaces"
        }
        candidate_generator_params["entity_indexers"]["wordnet"]["tokenizer"] = {
            "type": "just_spaces"
        }

        self.tokenizer_and_candidate_generator = (
            build_tokenizer_and_candidate_generator()
        )
        knowbert_logger.info("Done building candidate generators")
        # self.tokenizer_and_candidate_generator = TokenizerAndCandidateGenerator.\
        #     from_params(Params(candidate_generator_params))

        # self.tokenizer_and_candidate_generator = BertTokenizerAndCandidateGenerator(
        #    entity_candidate_generators=,
        #    entity_indexers=,
        #    bert_model_type='bert-base-uncased',
        #    do_lower_case=True,
        #    whitespace_tokenize=
        # )
        self.tokenizer_and_candidate_generator.whitespace_tokenize = False

        assert masking_strategy is None or masking_strategy == "full_mask"
        self.masking_strategy = masking_strategy

        # need bert_tokenizer_and_candidate_generator
        self.entity_vocab = Vocabulary.from_files(
            directory="https://allennlp.s3-us-west-2.amazonaws.com/knowbert/models/vocabulary_wordnet_wiki.tar.gz"
        )
        self.vocab = Vocabulary.from_pretrained_transformer(
            model_name="bert-base-uncased"
        )
        self.vocab.extend_from_vocab(self.entity_vocab)
        # self.vocab = Vocabulary.from_params(vocab_params)

        # self.iterator = DataIterator.from_params(
        #     Params({"type": "basic", "batch_size": batch_size})
        # )
        # self.iterator.index_with(self.vocab)

    def _replace_mask(self, s):
        return s.replace("[MASK]", " [MASK] ")

    def iter_batches(
        self,
        sentences_or_sentence_pairs: Union[List[str], List[List[str]]],
        verbose=True,
    ):
        # create instances
        instances = []
        for sentence_or_sentence_pair in sentences_or_sentence_pairs:
            if isinstance(sentence_or_sentence_pair, list):
                assert len(sentence_or_sentence_pair) == 2
                tokens_candidates = self.tokenizer_and_candidate_generator.tokenize_and_generate_candidates(
                    self._replace_mask(sentence_or_sentence_pair[0]),
                    self._replace_mask(sentence_or_sentence_pair[1]),
                )
            else:
                tokens_candidates = self.tokenizer_and_candidate_generator.tokenize_and_generate_candidates(
                    self._replace_mask(sentence_or_sentence_pair)
                )

            knowbert_logger.debug(f"token_candidates: {tokens_candidates}")

            if verbose:
                knowbert_logger.debug(self._replace_mask(sentence_or_sentence_pair))
                knowbert_logger.debug(tokens_candidates["tokens"])

            # now modify the masking if needed
            if self.masking_strategy == "full_mask":
                # replace the mask span with a @@mask@@ span
                masked_indices = [
                    index
                    for index, token in enumerate(tokens_candidates["tokens"])
                    if token == "[MASK]"
                ]

                spans_to_mask = {(i, i) for i in masked_indices}
                replace_candidates_with_mask_entity(
                    tokens_candidates["candidates"], spans_to_mask
                )

                # now mbert_vocabke sure the spans are actually masked
                for key in tokens_candidates["candidates"].keys():
                    for span_to_mask in spans_to_mask:
                        found = False
                        for span in tokens_candidates["candidates"][key][
                            "candidate_spans"
                        ]:
                            if tuple(span) == tuple(span_to_mask):
                                found = True
                        if not found:
                            tokens_candidates["candidates"][key][
                                "candidate_spans"
                            ].append(list(span_to_mask))
                            tokens_candidates["candidates"][key][
                                "candidate_entities"
                            ].append(["@@MASK@@"])
                            tokens_candidates["candidates"][key][
                                "candidate_entity_priors"
                            ].append([1.0])
                            tokens_candidates["candidates"][key][
                                "candidate_segment_ids"
                            ].append(0)
                            # hack, assume only one sentence
                            assert not isinstance(sentence_or_sentence_pair, list)

            fields = self.tokenizer_and_candidate_generator.convert_tokens_candidates_to_fields(
                tokens_candidates
            )
            # fields['tokens'].index(self.bert_vocab)
            knowbert_logger.debug(fields)
            instances.append(Instance(fields))

            knowbert_logger.debug(instances[-1])

        batch = Batch(instances)
        batch.index_instances(self.vocab)
        tensor_dict = batch.as_tensor_dict()

        # Fix tensor_dict
        # after index_instances tensor_dict['tokens'] has field 'tokens':{'tokens':...} instead of only 'tokens:...'
        tensor_dict["tokens"]["tokens"] = tensor_dict["tokens"]["tokens"]["tokens"]

        # wiki- and wordnet candidate_entities:ids have unecessary field 'token_charackters'
        tensor_dict["candidates"]["wiki"]["candidate_entities"]["ids"] = tensor_dict[
            "candidates"
        ]["wiki"]["candidate_entities"]["ids"]["token_characters"]

        tensor_dict["candidates"]["wordnet"]["candidate_entities"]["ids"] = tensor_dict[
            "candidates"
        ]["wordnet"]["candidate_entities"]["ids"]["token_characters"]

        # wiki and wordnet candidate_entities:ids are offset by 1 in new allennlp version
        # Only the @@Padding@@ token is not offset, hence the mask
        candidate_mask = (
            tensor_dict["candidates"]["wiki"]["candidate_entities"]["ids"] > 0
        ).type(torch.uint8)
        tensor_dict["candidates"]["wiki"]["candidate_entities"]["ids"] -= candidate_mask

        candidate_mask = (
            tensor_dict["candidates"]["wordnet"]["candidate_entities"]["ids"] > 0
        ).type(torch.uint8)
        tensor_dict["candidates"]["wordnet"]["candidate_entities"][
            "ids"
        ] -= candidate_mask

        yield tensor_dict
