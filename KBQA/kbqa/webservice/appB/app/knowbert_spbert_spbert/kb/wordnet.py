"""
Notes on wordnet ids:
    in KG embeddings, have both synset and lemma nodes:
        synsets are keyed by something like able.a.01register("wordnet_mention_generator")
        each synset has a number of lemmas, keyed by something like able%3:00:00::

    In WSD task, you are given (lemma, pos) and asked to predict the lemma
        key, e.g. (able, adj) -> which synset do we get?

    Internally, we use the able.a.01 key for synsets, but maintain a map
    from (lemma, pos, internal key) -> external key for evaluation with semcor.
"""


from collections import defaultdict
import logging
import random
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from allennlp.common.file_utils import cached_path
from allennlp.data import Token
import h5py
from app.knowbert_spbert_spbert.kb.common import EntityEmbedder
from app.knowbert_spbert_spbert.kb.common import get_empty_candidates
from app.knowbert_spbert_spbert.kb.common import init_bert_weights
from app.knowbert_spbert_spbert.kb.common import JsonFile
from app.knowbert_spbert_spbert.kb.common import MentionGenerator
from app.knowbert_spbert_spbert.kb.common import WhitespaceTokenizer
import spacy
import torch

knowbert_logger = logging.getLogger("knowbert-logger.wordnet")


class WordNetSpacyPreprocessor:
    """
    A "preprocessor" that really does POS tagging and lemmatization using spacy,
    plus some hand crafted rules.

    allennlp tokenizers take strings and return lists of Token classes.
    we'll run spacy first, then modify the POS / lemmas as needed, then
    return a new list of Token
    """

    def __init__(self, whitespace_tokenize_only: bool = False):
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner", "textcat"])
        if whitespace_tokenize_only:
            self.nlp.tokenizer = WhitespaceTokenizer(self.nlp.vocab)

        # spacy POS are similar, but not exactly the same as wordnet,
        # so need this conversion for tags that need to be mapped
        self.spacy_to_wordnet_map = {"PROPN": "NOUN"}

    def __call__(self, text: str) -> List[Token]:
        spacy_doc = self.nlp(text)
        # create allennlp tokens
        normalized_tokens = [
            Token(
                spacy_token.text,
                pos_=self.spacy_to_wordnet_map.get(spacy_token.pos_, spacy_token.pos_),
                lemma_=spacy_token.lemma_,
            )
            for spacy_token in spacy_doc
            if not spacy_token.is_space
        ]

        return normalized_tokens


def _norm_lemma(lemma_str: str) -> str:
    return lemma_str.replace("_", " ").replace("-", " ")


WORDNET_TO_SEMCOR_POS_MAP = {
    "n": "NOUN",  # %1
    "v": "VERB",  # %2
    "a": "ADJ",  # %3
    "r": "ADV",  # %4
    "s": "ADJ",  # %5
}


def load_candidate_maps(
    fname: str, topk: int = 30, count_smoothing: int = 1
) -> Tuple[Dict, Dict]:
    """
    Load the candidate maps from the entity file.

    entity_file is the jsonl dump from extract_wordnet.py

    returns:
        candidates[Dict[normalized lemma string] -> candidates
        lemma_id_to_synset_id = Dict["able%3:00:00"] -> "able.a.01"

    each value candidates list is:
        [candidate1_metadata, candidate2_metadata, etc]
    where candidate_metadata is a dict with keys:
            synset_id, lemma_id, pos (n, v, a,   ), prior

    The lemmas are underscore and hyphen normalized for training.

    topk = keep this many of the top candidates for each lemma
    count_smoothing = use this for smoothing
        if count_smoothing < 0 then don't normalize lemmas, just return raw counts
    """

    def _update(d: Dict, key: str, m: Dict) -> None:
        if key not in d:
            d[key] = []
        d[key].append(m)

    def _trim_and_normalize(d: Dict, num: int, smoothing: int) -> None:
        for key in d:
            all_candidates = d[key]
            if len(all_candidates) > num:
                # sort by count and trim
                # sorted sorts ascending by default, we want decending by count
                sorted_candidates = sorted(
                    all_candidates, key=lambda x: x["prior"], reverse=True
                )
                trimmed_candidates = sorted_candidates[:num]
            else:
                trimmed_candidates = all_candidates

            if smoothing >= 0:
                sum_count = sum(ele["prior"] + smoothing for ele in trimmed_candidates)
                for cand in trimmed_candidates:
                    cand["prior"] = (cand["prior"] + smoothing) / sum_count
            d[key] = trimmed_candidates

    candidates: Dict = {}
    lemma_id_to_synset_id: Dict = {}

    with JsonFile(cached_path(fname), "r") as fin:
        for entity in fin:
            if entity["type"] == "lemma":
                lemma_id = entity["id"]
                lemma_str = lemma_id.partition("%")[0]
                synset_id = entity["synset"]

                metadata = {
                    "synset_id": synset_id,
                    "lemma_id": lemma_id,
                    "pos": entity["pos"],
                    "prior": entity["count"],
                }

                # normalize the lemma_str
                lemma_str_normalized = _norm_lemma(lemma_str)
                _update(candidates, lemma_str_normalized, metadata)

                lemma_id_to_synset_id[lemma_id] = synset_id

    # now trim to top k and normalize the prior
    _trim_and_normalize(candidates, topk, count_smoothing)

    return candidates, lemma_id_to_synset_id


# Unsupervised setting for LM:
#   raw data -> use spacy to get lemma -> look up all candidates normalizing
#       - and _
#
# With annotated data:
#       at train time:
#           given gold spans and entity ids:
#               map semcor tokens to flat token sequence + gold ids + gold spans
#               look up all candidate spans using raw data approach ignoring POS and lemma
#               remove generic entity types
#               restrict candidate spans to just those that have annotated senses
#               compute the recall of gold span / entity from pruned candidate lsit (for MWE separate from single words)
#
#       at test time:
#           given gold POS and lemma, get candidates.
#           for generic entity types, use heuristic to restrict candidates
#           should have near 100% recall of gold span
#           and first sense baseline should be high


@MentionGenerator.register("wordnet_mention_generator")
class WordNetCandidateMentionGenerator(MentionGenerator):
    """
    Generate lists of candidate entities. Provides several methods that
    process input text of various format to produce mentions.

    Each text is represented by:
            {'tokenized_text': List[str],
             'candidate_spans': List[List[int]] list of (start, end) indices for candidates,
                    where span is tokenized_text[start:(end + 1)]
             'candidate_entities': List[List[str]] = for each entity,
                    the candidates to link to. value is synset id, e.g
                    able.a.02 or hot_dog.n.01
             'candidate_entity_priors': List[List[float]]
        }
    """

    def __init__(
        self,
        entity_file: str,
        max_entity_length: int = 7,
        max_number_candidates: int = 30,
        count_smoothing: int = 1,
        use_surface_form: bool = False,
        random_candidates: bool = False,
    ):

        self._raw_data_processor = WordNetSpacyPreprocessor()
        self._raw_data_processor_whitespace = WordNetSpacyPreprocessor(
            whitespace_tokenize_only=True
        )

        self._candidate_list, self._lemma_to_synset = load_candidate_maps(
            entity_file, count_smoothing=-1
        )
        # candidate_list[hog dog] -> [all candidate lemmas]

        self._entity_synsets = {
            # 'location%1:03:00::': 'location.n.01',  # (LOC)
            # 'person%1:03:00::': 'person.n.01',    # (PER)
            # 'group%1:03:00::': 'group.n.01'      # (ORG)
            "location": "location.n.01",  # (LOC)
            "person": "person.n.01",  # (PER)
            "group": "group.n.01",  # (ORG)
        }
        self._entity_lemmas = {
            "location%1:03:00::",
            "person%1:03:00::",
            "group%1:03:00::",
        }

        self._max_entity_length = max_entity_length
        self._max_number_candidates = max_number_candidates
        self._count_smoothing = count_smoothing
        self._use_surface_form = use_surface_form

        self._random_candidates = random_candidates
        if self._random_candidates:
            self._unique_synsets = list(set(self._lemma_to_synset.values()))

    def get_mentions_raw_text(
        self,
        text: str,
        whitespace_tokenize: bool = False,
        allow_empty_candidates: bool = False,
    ) -> Dict[str, Any]:
        """
        returns:
            {'tokenized_text': List[str],
             'candidate_spans': List[List[int]] list of (start, end) indices for candidates,
                    where span is tokenized_text[start:(end + 1)]
             'candidate_entities': List[List[str]] = for each entity,
                    the candidates to link to. value is synset id, e.g
                    able.a.02 or hot_dog.n.01
             'candidate_entity_priors': List[List[float]]
        }
        """

        if whitespace_tokenize:
            tokenized = self._raw_data_processor_whitespace(text)
        else:
            tokenized = self._raw_data_processor(text)

        tokenized_text = [token.text for token in tokenized]

        # will look up by both lemma (and the tokenized text if use_surface_form)
        # lowercase and remove '.'
        lemmas = [token.lemma_.lower().replace(".", "") for token in tokenized]
        clist = [lemmas]
        if self._use_surface_form:
            normed_tokens = [token.lower().replace(".", "") for token in tokenized_text]
            clist.append(normed_tokens)
            # remove ones that match the lemma
            # filtered_tokens = [None if t == l else t for l, t in  zip(lemmas, normed_tokens)]
            # clist.append(filtered_tokens)

        # look for candidates
        # 1. create lemma string key
        # 2. look up candidates
        # 3. combine candidates from lemmas and tokens
        # 4. sort and normalize the candidates

        # keep track of the candidates hashed by (start, end) indices
        # (start, end) -> [list of candidate dicts that will be sorted / normalized]
        candidates_by_span = defaultdict(lambda: list())
        n = len(tokenized_text)
        for start in range(n):
            for end in range(start, min(n, start + self._max_entity_length - 1)):
                for ci, cc in enumerate(clist):
                    # only consider strings that don't begin/end with '-'
                    # and surface forms that are different from lemmas
                    if (
                        cc[start] != "-"
                        and cc[end] != "-"
                        and (
                            ci == 0
                            or cc[start : (end + 1)] != lemmas[start : (end + 1)]
                        )
                    ):
                        candidate_lemma = " ".join(
                            [t for t in cc[start : (end + 1)] if t != "-"]
                        )
                        if candidate_lemma in self._candidate_list:
                            candidate_metadata = self._candidate_list[candidate_lemma]
                            span_key = (start, end)
                            candidates_by_span[span_key].extend(candidate_metadata)

        # trim and normalize the candidates
        candidate_spans = []
        candidate_entities = []
        candidate_entity_priors = []
        for span_key, s_candidates in candidates_by_span.items():
            if len(s_candidates) > self._max_number_candidates:
                # sort by count and trim
                # sorted sorts ascending by default, we want decending by count
                sorted_candidates = sorted(
                    s_candidates, key=lambda x: x["prior"], reverse=True
                )
                trimmed_candidates = sorted_candidates[: self._max_number_candidates]
            else:
                trimmed_candidates = s_candidates

            # normalize the counts
            sum_count = sum(
                ele["prior"] + self._count_smoothing for ele in trimmed_candidates
            )
            candidate_spans.append([span_key[0], span_key[1]])
            candidate_entities.append([c["synset_id"] for c in trimmed_candidates])
            candidate_entity_priors.append(
                [
                    (c["prior"] + self._count_smoothing) / sum_count
                    for c in trimmed_candidates
                ]
            )

        if self._random_candidates:
            # randomly replace the candidate_entities
            for i in range(len(candidate_entities)):
                rand_candidates = list(candidate_entities[i])
                for j in range(len(rand_candidates)):
                    rand_candidate = random.choice(self._unique_synsets)
                    rand_candidates[j] = rand_candidate
                candidate_entities[i] = rand_candidates

        ret = {
            "tokenized_text": tokenized_text,
            "candidate_spans": candidate_spans,
            "candidate_entities": candidate_entities,
            "candidate_entity_priors": candidate_entity_priors,
        }

        if not allow_empty_candidates and len(candidate_spans) == 0:
            # no candidates found, substitute the padding entity id
            ret.update(get_empty_candidates())

        return ret


@EntityEmbedder.register("wordnet_all_embeddings")
class WordNetAllEmbedding(torch.nn.Module, EntityEmbedder):
    """
    Combines pretrained fixed embeddings with learned POS embeddings.

    Given entity candidate list:
        - get list of unique entity ids
        - look up
        - concat POS embedding
        - linear project
        - remap to candidate embedding shape
    """

    POS_MAP = {
        "@@PADDING@@": 0,
        "n": 1,
        "v": 2,
        "a": 3,
        "r": 4,
        "s": 5,
        # have special POS embeddings for mask / null, so model can learn
        # it's own representation for them
        "@@MASK@@": 6,
        "@@NULL@@": 7,
        "@@UNKNOWN@@": 8,
    }

    def __init__(
        self,
        embedding_file: str,
        entity_dim: int,
        entity_file: str = "",
        vocab_file: str = "",
        entity_h5_key: str = "conve_tucker_infersent_bert",
        dropout: float = 0.1,
        pos_embedding_dim: int = 25,
        include_null_embedding: bool = False,
    ):
        """
        pass pos_emedding_dim = None to skip POS embeddings and all the
            entity stuff, using this as a pretrained embedding file
            with feedforward
        """

        super().__init__()
        if pos_embedding_dim is not None:
            # entity_id -> pos abbreviation, e.g.
            # 'cat.n.01' -> 'n'
            # includes special, e.g. '@@PADDING@@' -> '@@PADDING@@'
            entity_to_pos = {}
            with JsonFile(cached_path(entity_file), "r") as fin:
                for node in fin:
                    if node["type"] == "synset":
                        entity_to_pos[node["id"]] = node["pos"]
            for special in ["@@PADDING@@", "@@MASK@@", "@@NULL@@", "@@UNKNOWN@@"]:
                entity_to_pos[special] = special

            # list of entity ids
            entities = ["@@PADDING@@"]
            with open(cached_path(vocab_file), "r") as fin:
                for line in fin:
                    entities.append(line.strip())

            # the map from entity index id -> pos embedding id,
            # will use for POS embedding lookup
            entity_id_to_pos_index = [
                self.POS_MAP[entity_to_pos[ent]] for ent in entities
            ]
            self.register_buffer(
                "entity_id_to_pos_index", torch.tensor(entity_id_to_pos_index)
            )
            self.pos_embeddings = torch.nn.Embedding(len(entities), pos_embedding_dim)
            init_bert_weights(self.pos_embeddings, 0.02)

            self.use_pos = True
        else:
            self.use_pos = False

        # load the embeddings
        with h5py.File(cached_path(embedding_file), "r") as fin:
            entity_embeddings = fin[entity_h5_key][...]
        self.entity_embeddings = torch.nn.Embedding(
            entity_embeddings.shape[0], entity_embeddings.shape[1], padding_idx=0
        )
        self.entity_embeddings.weight.data.copy_(
            torch.tensor(entity_embeddings).contiguous()
        )

        if pos_embedding_dim is not None:
            assert entity_embeddings.shape[0] == len(entities)
            concat_dim = entity_embeddings.shape[1] + pos_embedding_dim
        else:
            concat_dim = entity_embeddings.shape[1]

        self.proj_feed_forward = torch.nn.Linear(concat_dim, entity_dim)
        init_bert_weights(self.proj_feed_forward, 0.02)

        self.dropout = torch.nn.Dropout(dropout)

        self.entity_dim = entity_dim

        self.include_null_embedding = include_null_embedding
        if include_null_embedding:
            # a special embedding for null
            entities = ["@@PADDING@@"]
            with open(cached_path(vocab_file), "r") as fin:
                for line in fin:
                    entities.append(line.strip())
            self.null_id = entities.index("@@NULL@@")
            self.null_embedding = torch.nn.Parameter(torch.zeros(entity_dim))
            self.null_embedding.data.normal_(mean=0.0, std=0.02)

    def get_output_dim(self) -> int:
        return self.entity_dim

    def get_null_embedding(self) -> torch.nn.Parameter:
        return self.null_embedding

    def forward(self, entity_ids: torch.Tensor) -> torch.Tensor:
        """
        entity_ids = (batch_size, num_candidates, num_entities) array of entity
            ids

        returns (batch_size, num_candidates, num_entities, embed_dim)
            with entity embeddings
        """
        # get list of unique entity ids
        unique_ids, unique_ids_to_entity_ids = torch.unique(
            entity_ids, return_inverse=True
        )
        # unique_ids[unique_ids_to_entity_ids].reshape(entity_ids.shape)

        # look up (num_unique_embeddings, full_entity_dim)
        unique_entity_embeddings = self.entity_embeddings(
            unique_ids.contiguous()
        ).contiguous()

        # get POS tags from entity ids (form entity id -> pos id embedding)
        # (num_unique_embeddings)
        if self.use_pos:
            weights = self.entity_id_to_pos_index.reshape(-1, 1)
            unique_pos_ids = torch.nn.functional.embedding(
                unique_ids, weights
            ).contiguous()
            # unique_pos_ids = torch.nn.functional.embedding(unique_ids, self.entity_id_to_pos_index).contiguous()
            # (num_unique_embeddings, pos_dim)
            unique_pos_embeddings = (
                self.pos_embeddings(unique_pos_ids).contiguous().squeeze()
            )
            knowbert_logger.debug(unique_pos_embeddings)
            # concat
            entity_and_pos = torch.cat(
                [unique_entity_embeddings, unique_pos_embeddings], dim=-1
            )
        else:
            entity_and_pos = unique_entity_embeddings

        # run the ff
        # (num_embeddings, entity_dim)
        projected_entity_and_pos = self.dropout(
            self.proj_feed_forward(entity_and_pos.contiguous())
        )

        # replace null if needed
        if self.include_null_embedding:
            null_mask = unique_ids == self.null_id
            projected_entity_and_pos[null_mask] = self.null_embedding

        # remap to candidate embedding shape
        return projected_entity_and_pos[unique_ids_to_entity_ids].contiguous()
