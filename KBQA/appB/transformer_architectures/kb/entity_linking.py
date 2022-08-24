"""
 Entity linking:
   Input = sequence of tokens
   Output = list of spans + entity id of linked entity
       span_indices = (batch_size, max_num_spans, 2)
       entity_id = (batch_size, max_num_spans)

 Proceeds in two steps:
   (1) candidate mention generation = generate a list of spans and possible
       candidate entitys to link to
   (2) disambiguated entity to predict


Model component is split into several sub-components.

 Candidate mention generation is off loaded to data generators, and uses
 pre-processing, dictionaries, and rules.

 EntityDisambiguation: a module that takes contextualized vectors, candidate
   spans (=mention boundaries, and candidate entity ids to link to),
   candidate entity priors and returns predicted probability for each candiate.

 EntityLinkingWithCandidateMentions: a Model that encapusulates:
   a LM that contextualizes token ids
   a EntityDisambiguation that predicts candidate mentions from LM context vectors
   a loss calculation for optimizing
   (optional) a KG embedding model that can be used for multitasking entity
        embeddings and the entity linker
"""


# tokenization notes:
#
# BERT tokenization:
#    - apply word tokenization
#    - apply subword tokenization
#    - truncate length
#    - add [CLS] text a [SEP]   OR   [CLS] text a [SEP] text b [SEP]
#
# For entity candidate generation, or annotated spans for entity linking
#   or NER or ...
#
# Original data is word tokenized starting with index 0 as first word.
# Original data can have [SEP] in middle but SHOULD NOT have [CLS] or terminal [SEP].
#
# Then use "bert-pretrained" token indexer from allennlp with "use_starting_offsets": True:
# {
#        "type": "bert-pretrained",
#        "pretrained_model": "tests/fixtures/bert/vocab.txt",
#        "do_lowercase": True,
#        "use_starting_offsets": True,
#        "max_pieces": 512,
#    }
# This will add [CLS] and [SEP] to original data, so first offset index will
#   be 1
#
# Should ideally do the original tokenization with the bert word splitter,
# or if orginal annotation is word split already re-tokenize it.

from typing import Dict
from typing import List

from allennlp.common.registrable import Registrable
from allennlp.data import DatasetReader
from allennlp.data import Tokenizer
from allennlp.data import Vocabulary
from allennlp.data.token_indexers import TokenCharactersIndexer
from allennlp.data.token_indexers import TokenIndexer
from allennlp.models import Model
from allennlp.nn.regularizers import RegularizerApplicator
from KBQA.appB.transformer_architectures.kb.common import F1Metric
from KBQA.appB.transformer_architectures.kb.common import get_dtype_for_module
import torch


@TokenIndexer.register("characters_tokenizer")
class TokenCharactersIndexerTokenizer(TokenCharactersIndexer):
    @classmethod
    def from_params(cls, params: Dict) -> "TokenCharactersIndexerTokenizer":
        tokenizer = Tokenizer.from_params(params.pop("tokenizer"))
        ret = TokenCharactersIndexer.from_params(params)
        ret._character_tokenizer = tokenizer
        return ret


class EntityLinkingReader(DatasetReader, Registrable):
    """
    Each instance is a context of text, gold mention spans, and gold entity id.

    This is converted to tensors:
        tokens: dict -> token id from the token indexer (batch_size, num_times)
        candidate_spans: -> list of (start, end) indices of each span to make
            a prediction for, (batch_size, num_spans, 2)
        candidate_entites: -> list of candidate entity ids for each span,
            (batch_size, num_spans, num_candidates)
        gold_entities: list of gold entity id for span (batch_size, num_spans, 1)

    The model makes a prediction for each span in candidate_spans.
    Depending on whether it's desirable to use gold entity spans or have
    the model predict spans will determine whether to pass gold spans as
    candidate_spans or pass many candidate spans that have NULL entity.


    tokens is a TextField
    candidate_spans is a spanfield
    candidate_entities is a TextField that we use a vocabulary to
        do the indexing
    gold_entities is a text field
    """

    pass


class BaseEntityDisambiguator(Registrable):
    pass


class EntityLinkingBase(Model):
    def __init__(
        self,
        vocab: Vocabulary,
        margin: float = 0.2,
        decode_threshold: float = 0.0,
        loss_type: str = "margin",
        namespace: str = "entity",
        regularizer: RegularizerApplicator = None,
    ):

        super().__init__(vocab, regularizer)

        if loss_type == "margin":
            self.loss = torch.nn.MarginRankingLoss(margin=margin)
            self.decode_threshold = decode_threshold
        elif loss_type == "softmax":
            self.loss = torch.nn.NLLLoss(ignore_index=-100)
            # set threshold to small value so we just take argmax
            self._log_softmax = torch.nn.LogSoftmax(dim=-1)
            self.decode_threshold = -990
        else:
            raise ValueError("invalid loss type, got {}".format(loss_type))
        self.loss_type = loss_type

        self.null_entity_id = self.vocab.get_token_index("@@NULL@@", namespace)
        assert self.null_entity_id != self.vocab.get_token_index(
            "@@UNKNOWN@@", namespace
        )

        self._f1_metric = F1Metric()
        self._f1_metric_untyped = F1Metric()

    def _compute_f1(
        self,
        linking_scores: torch.Tensor,
        candidate_spans: torch.Tensor,
        candidate_entities: torch.Tensor,
        gold_entities: torch.Tensor,
    ) -> None:
        # will call F1Metric with predicted and gold entities encoded as
        # [(start, end), entity_id]

        predicted_entities = self._decode(
            linking_scores, candidate_spans, candidate_entities
        )

        # make a mask of valid predictions and non-null entities to select
        # ids and spans
        # (batch_size, num_spans, 1)
        gold_mask = (gold_entities > 0) & (gold_entities != self.null_entity_id)

        valid_gold_entity_spans = (
            candidate_spans[torch.cat([gold_mask, gold_mask], dim=-1)]
            .view(-1, 2)
            .tolist()
        )
        valid_gold_entity_id = gold_entities[gold_mask].tolist()

        batch_size, num_spans, _ = linking_scores.shape
        batch_indices = (
            torch.arange(batch_size)
            .unsqueeze(-1)
            .repeat([1, num_spans])[gold_mask.squeeze(-1).cpu()]
        )

        gold_entities_for_f1: List = []
        predicted_entities_for_f1: List = []
        gold_spans_for_f1: List = []
        predicted_spans_for_f1: List = []
        for k in range(batch_size):
            gold_entities_for_f1.append([])
            predicted_entities_for_f1.append([])
            gold_spans_for_f1.append([])
            predicted_spans_for_f1.append([])

        for gi, gs, g_batch_index in zip(
            valid_gold_entity_id, valid_gold_entity_spans, batch_indices.tolist()
        ):
            gold_entities_for_f1[g_batch_index].append((tuple(gs), gi))
            gold_spans_for_f1[g_batch_index].append((tuple(gs), "ENT"))

        for p_batch_index, ps, pi in predicted_entities:
            span = tuple(ps)
            predicted_entities_for_f1[p_batch_index].append((span, pi))
            predicted_spans_for_f1[p_batch_index].append((span, "ENT"))

        self._f1_metric_untyped(predicted_spans_for_f1, gold_spans_for_f1)
        self._f1_metric(predicted_entities_for_f1, gold_entities_for_f1)

    def _decode(
        self,
        linking_scores: torch.Tensor,
        candidate_spans: torch.Tensor,
        candidate_entities: torch.Tensor,
    ) -> List:
        # returns [[batch_index1, (start1, end1), eid1],
        #          [batch_index2, (start2, end2), eid2], ...]

        # Note: We assume that linking_scores has already had the mask
        # applied such that invalid candidates have very low score. As a result,
        # we don't need to worry about masking the valid candidate spans
        # here, since their score will be very low, and won't exceed
        # the threshold.

        # find maximum candidate entity score in each valid span
        # (batch_size, num_spans), (batch_size, num_spans)
        max_candidate_score, max_candidate_indices = linking_scores.max(dim=-1)

        # get those above the threshold
        above_threshold_mask = max_candidate_score > self.decode_threshold

        # for entities with score > threshold:
        #       get original candidate span
        #       get original entity id
        # (num_extracted_spans, 2)
        extracted_candidates = candidate_spans[above_threshold_mask]
        # (num_extracted_spans, num_candidates)
        candidate_entities_for_extracted_spans = candidate_entities[
            above_threshold_mask
        ]
        extracted_indices = max_candidate_indices[above_threshold_mask]
        # the batch number (num_extracted_spans, )
        batch_size, num_spans, _ = linking_scores.shape
        batch_indices = (
            torch.arange(batch_size)
            .unsqueeze(-1)
            .repeat([1, num_spans])[above_threshold_mask.cpu()]
        )

        extracted_entity_ids = []
        for k, ind in enumerate(extracted_indices):
            extracted_entity_ids.append(candidate_entities_for_extracted_spans[k, ind])

        # make tuples [(span start, span end), id], ignoring the null entity
        ret = []
        for start_end, eid, batch_index in zip(
            extracted_candidates.tolist(), extracted_entity_ids, batch_indices.tolist()
        ):
            entity_id = eid.item()
            if entity_id != self.null_entity_id:
                ret.append((batch_index, tuple(start_end), entity_id))

        return ret

    def get_metrics(self, reset: bool = False) -> Dict:
        precision, recall, f1_measure = self._f1_metric.get_metric(reset)
        (
            precision_span,
            recall_span,
            f1_measure_span,
        ) = self._f1_metric_untyped.get_metric(reset)
        metrics = {
            "el_precision": precision,
            "el_recall": recall,
            "el_f1": f1_measure,
            "span_precision": precision_span,
            "span_recall": recall_span,
            "span_f1": f1_measure_span,
        }

        return metrics

    def _compute_loss(
        self,
        candidate_entities: torch.Tensor,
        candidate_spans: torch.Tensor,
        linking_scores: torch.Tensor,
        gold_entities: torch.Tensor,
    ) -> Dict:

        if self.loss_type == "margin":
            return self._compute_margin_loss(
                candidate_entities, candidate_spans, linking_scores, gold_entities
            )
        elif self.loss_type == "softmax":
            return self._compute_softmax_loss(
                candidate_entities, candidate_spans, linking_scores, gold_entities
            )
        else:
            return {"loss": f"Unknown self.loss_type = {self.loss_type}!"}

    def _compute_margin_loss(
        self,
        candidate_entities: torch.Tensor,
        candidate_spans: torch.Tensor,
        linking_scores: torch.Tensor,
        gold_entities: torch.Tensor,
    ) -> Dict:

        # compute loss
        # in End-to-End Neural Entity Linking
        # loss = max(0, gamma - score) if gold mention
        # loss = max(0, score) if not gold mention
        #
        # torch.nn.MaxMarginLoss(x1, x2, y) = max(0, -y * (x1 - x2) + gamma)
        #   = max(0, -x1 + x2 + gamma)  y = +1
        #   = max(0, gamma - x1) if x2 == 0, y=+1
        #
        #   = max(0, x1 - gamma) if y==-1, x2=0

        candidate_mask = candidate_entities > 0
        # (num_entities, )
        non_masked_scores = linking_scores[candidate_mask]

        # broadcast gold ids to all candidates
        num_candidates = candidate_mask.shape[-1]
        # (batch_size, num_spans, num_candidates)
        broadcast_gold_entities = gold_entities.repeat(1, 1, num_candidates)
        # compute +1 / -1 labels for whether each candidate is gold
        positive_labels = (broadcast_gold_entities == candidate_entities).long()
        negative_labels = (broadcast_gold_entities != candidate_entities).long()
        labels = (positive_labels - negative_labels).to(
            dtype=get_dtype_for_module(self)
        )
        # finally select the non-masked candidates
        # (num_entities, ) with +1 / -1
        non_masked_labels = labels[candidate_mask]

        loss = self.loss(
            non_masked_scores, torch.zeros_like(non_masked_labels), non_masked_labels
        )

        # metrics
        self._compute_f1(
            linking_scores, candidate_spans, candidate_entities, gold_entities
        )

        return {"loss": loss}

    def _compute_softmax_loss(
        self,
        candidate_entities: torch.Tensor,
        candidate_spans: torch.Tensor,
        linking_scores: torch.Tensor,
        gold_entities: torch.Tensor,
    ) -> Dict:

        # compute log softmax
        # linking scores is already masked with -1000 in invalid locations
        # (batch_size, num_spans, max_num_candidates)
        log_prob = self._log_softmax(linking_scores)

        # get the valid scores.
        # needs to be index into the last time of log_prob, with -100
        # for missing values
        num_candidates = log_prob.shape[-1]
        # (batch_size, num_spans, num_candidates)
        broadcast_gold_entities = gold_entities.repeat(1, 1, num_candidates)

        # location of the positive label
        positive_labels = (broadcast_gold_entities == candidate_entities).long()
        # index of the positive class
        targets = positive_labels.argmax(dim=-1)

        # fill in the ignore class
        # DANGER: we assume that each instance has exactly one gold
        # label, and that padded instances are ones for which all
        # candidates are invalid
        # (batch_size, num_spans)
        invalid_prediction_mask = (candidate_entities != 0).long().sum(dim=-1) == 0
        targets[invalid_prediction_mask] = -100

        loss = self.loss(
            log_prob.view(-1, num_candidates),
            targets.view(
                -1,
            ),
        )

        # metrics
        self._compute_f1(
            linking_scores, candidate_spans, candidate_entities, gold_entities
        )

        return {"loss": loss}
