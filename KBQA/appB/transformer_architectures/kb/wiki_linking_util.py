import json
import logging
import random
import time
from typing import Any
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
from typing import Union

from allennlp.common.file_utils import cached_path
from allennlp.data.dataset_readers.dataset_utils import enumerate_spans
from KBQA.appB.transformer_architectures.kb.common import get_empty_candidates
from KBQA.appB.transformer_architectures.kb.common import MentionGenerator
from KBQA.appB.transformer_architectures.kb.common import WhitespaceTokenizer
import spacy
from spacy.lang.char_classes import LIST_CURRENCY
from spacy.lang.char_classes import LIST_ELLIPSES
from spacy.lang.char_classes import LIST_PUNCT
from spacy.lang.char_classes import LIST_QUOTES
from spacy.lang.en import STOP_WORDS

knowbert_logger = logging.getLogger("knowbert-logger.wiki")


def prior_entity_candidates(
    candidates_file: str,
    max_candidates: int = 30,
    allowed_entities_set: Union[None, Set] = None,
    max_mentions: Union[None, int] = None,
) -> Tuple[Dict, Dict, Dict]:
    """
    Args:
    cand_ent_num: how many candidate entities to keep for each mention
    allowed_entities_set: restrict the candidate entities to only this set. for example
    the most frequent 1M entities. First this restiction applies and then the cand_ent_num.
    """
    wall_start = time.time()
    p_e_m: Dict = {}  # for each mention we have a list of tuples (ent_id, score)
    # for each mention of the p_e_m we store the total freq
    # this will help us decide which cand entities to take
    mention_total_freq: Dict = {}
    p_e_m_errors = 0
    incompatible_ent_ids = 0
    duplicate_mentions_cnt = 0
    clear_conflict_winner = 0  # both higher absolute frequency and longer cand list
    not_clear_conflict_winner = 0  # higher absolute freq but shorter cand list
    with open(candidates_file) as fin:

        for i, line in enumerate(fin):

            if max_mentions is not None and i > max_mentions:
                break
            line = line.rstrip()
            line_parts = line.split("\t")
            mention = line_parts[0]
            absolute_freq = int(line_parts[1])
            entities = line_parts[2:]
            entity_candidates: List[Tuple] = []
            for e in entities:
                if len(entity_candidates) >= max_candidates:
                    break
                ent_id, score, name = [x.strip() for x in e.split(",", 2)]
                if (
                    allowed_entities_set is not None
                    and name not in allowed_entities_set
                ):
                    pass
                else:
                    entity_candidates.append((ent_id, name, float(score)))
            if entity_candidates:
                if mention in p_e_m:
                    duplicate_mentions_cnt += 1
                    # print("duplicate mention: ", mention)
                    if absolute_freq > mention_total_freq[mention]:
                        if len(entity_candidates) > len(p_e_m[mention]):
                            clear_conflict_winner += 1
                        else:
                            not_clear_conflict_winner += 1
                        p_e_m[mention] = entity_candidates
                        mention_total_freq[mention] = absolute_freq
                else:
                    # for each mention we have a list of tuples (ent_id, name, score)
                    p_e_m[mention] = entity_candidates
                    mention_total_freq[mention] = absolute_freq

    knowbert_logger.info(f"duplicate_mentions_cnt: {duplicate_mentions_cnt}")
    knowbert_logger.info(
        f"end of p_e_m reading. wall time: {(time.time() - wall_start) / 60} minutes"
    )
    knowbert_logger.info(f"p_e_m_errors: {p_e_m_errors}")
    knowbert_logger.info(f"incompatible_ent_ids: {incompatible_ent_ids}")

    wall_start = time.time()
    # two different p(e|m) mentions can be the same after lower() so we merge the two candidate
    # entities lists. But the two lists can have the same candidate entity with different score
    # we keep the highest score. For example if "Obama" mention gives 0.9 to entity Obama and
    # OBAMA gives 0.7 then we keep the 0.9 . Also we keep as before only the cand_ent_num entities
    # with the highest score

    p_e_m_lowercased: Dict = {}
    for mention, candidates in p_e_m.items():
        l_mention = mention.lower()
        lower_candidates = p_e_m.get(l_mention, [])
        combined_candidates: Dict = {}

        for cand in candidates + lower_candidates:
            if cand[0] in combined_candidates:
                if cand[2] > combined_candidates[cand[0]][2]:
                    combined_candidates[0] = cand

            else:
                combined_candidates[cand[0]] = cand

        combined_candidates_list = list(combined_candidates.values())
        sorted_candidates = sorted(
            combined_candidates_list, key=lambda x: x[2], reverse=True
        )

        p_e_m_lowercased[l_mention] = sorted_candidates[:max_candidates]

    return p_e_m, p_e_m_lowercased, mention_total_freq


STOP_SYMBOLS = set().union(LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, LIST_CURRENCY)


def span_filter_func(span: List[str]) -> bool:
    """
    This function halves the number of suggested mention spans whilst not affecting
    gold span recall at all. It can probably be improved further.
    """
    if span[0] in STOP_WORDS or span[-1] in STOP_WORDS:
        return False

    if any([c in STOP_SYMBOLS for c in span]):
        return False
    return True


@MentionGenerator.register("wiki")
class WikiCandidateMentionGenerator(MentionGenerator):

    defaults = {
        "candidates_file": "https://allennlp.s3-us-west-2.amazonaws.com/knowbert/wiki_entity_linking/prob_yago_crosswikis_wikipedia_p_e_m.txt",
        "wiki_file": "https://allennlp.s3-us-west-2.amazonaws.com/knowbert/wiki_entity_linking/wiki_name_id_map.txt",
        "redirections_file": "https://allennlp.s3-us-west-2.amazonaws.com/knowbert/wiki_entity_linking/wiki_redirects.txt",
        "disambiguations_file": "https://allennlp.s3-us-west-2.amazonaws.com/knowbert/wiki_entity_linking/wiki_disambiguation_pages.txt",
        "entity_world_path": "https://allennlp.s3-us-west-2.amazonaws.com/knowbert/wiki_entity_linking/wiki_id_to_string.json",
    }

    def __init__(
        self,
        candidates_file: str = "",
        entity_world_path: str = "",
        lowercase_candidates: bool = True,
        random_candidates: bool = False,
        pickle_cache_file: str = "",
    ):

        self.tokenizer = spacy.load(
            "en_core_web_sm", disable=["parser", "ner", "textcat"]
        )
        self.whitespace_tokenizer = spacy.load(
            "en_core_web_sm", disable=["parser", "ner", "textcat"]
        )
        self.whitespace_tokenizer.tokenizer = WhitespaceTokenizer(
            self.whitespace_tokenizer.vocab
        )

        self.random_candidates = random_candidates
        self.lowercase_candidates = lowercase_candidates

        if isinstance(entity_world_path, dict):
            self.entity_world: Dict = entity_world_path
        else:
            entity_world_path = cached_path(
                entity_world_path or self.defaults["entity_world_path"]
            )
            self.entity_world = json.load(open(entity_world_path))

        if pickle_cache_file:
            import pickle

            with open(cached_path(pickle_cache_file), "rb") as fin:
                data = pickle.load(fin)
            self.p_e_m = data["p_e_m"]
            self.p_e_m_low = data["p_e_m_low"]
            self.mention_total_freq = data["mention_total_freq"]
        else:
            valid_candidates_with_vectors = set(self.entity_world.keys())
            candidates_file = cached_path(
                candidates_file or self.defaults["candidates_file"]
            )
            (
                self.p_e_m,
                self.p_e_m_low,
                self.mention_total_freq,
            ) = prior_entity_candidates(
                candidates_file, allowed_entities_set=valid_candidates_with_vectors
            )

        self.random_candidates = random_candidates
        if self.random_candidates:
            self.p_e_m_keys_for_sampling = list(self.p_e_m.keys())

    def get_mentions_raw_text(
        self, text: str, whitespace_tokenize: bool = False
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
            tokens = self.whitespace_tokenizer(text)
        else:
            tokens = self.tokenizer(text)

        tokens = [t.text for t in tokens]
        all_spans = enumerate_spans(
            tokens, max_span_width=5, filter_function=span_filter_func
        )

        spans_to_candidates = {}

        for span in all_spans:
            candidate_entities = self.process(tokens[span[0] : span[1] + 1])
            if candidate_entities:
                # Only keep spans which we have candidates for.
                spans_to_candidates[(span[0], span[1])] = candidate_entities

        spans = []
        entities = []
        priors = []
        for span, candidates in spans_to_candidates.items():
            spans.append(list(span))
            entities.append([x[1] for x in candidates])
            mention_priors = [x[2] for x in candidates]

            # priors may not be normalized because we merged the
            # lowercase + cased values.
            sum_priors = sum(mention_priors)
            priors.append([x / sum_priors for x in mention_priors])

        ret = {
            "tokenized_text": tokens,
            "candidate_spans": spans,
            "candidate_entities": entities,
            "candidate_entity_priors": priors,
        }

        if len(spans) == 0:
            ret.update(get_empty_candidates())

        return ret

    def process(
        self, span: Union[List[str], str], lower: bool = False
    ) -> List[Tuple[str, str, float]]:
        """
        Look up spans in the candidate dictionary, including looking for
        a title format version of the same string. Returns a list of
        (entity_id, entity_candidate, p(entity_candidate | mention string)) pairs.
        """
        if self.random_candidates:
            random_key = random.choice(self.p_e_m_keys_for_sampling)
            return self.p_e_m[random_key]

        if isinstance(span, list):
            span = " ".join(span)

        # Makes all first chars of words uppercase, eg barack obama -> Barack Obama.
        title = span.title()
        title_freq = self.mention_total_freq.get(title, 0)
        span_freq = self.mention_total_freq.get(span, 0)

        if title_freq == 0 and span_freq == 0:
            if lower and span.lower() in self.p_e_m:
                return self.p_e_m[span.lower()]
            elif self.lowercase_candidates and span.lower() in self.p_e_m_low:
                return self.p_e_m_low[span.lower()]
            else:
                return []
        else:
            if span_freq > title_freq:
                return self.p_e_m[span]
            else:
                return self.p_e_m[title]


if __name__ == "__main__":

    finder = WikiCandidateMentionGenerator()
