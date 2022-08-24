""" Metric class for tracking correlations by saving predictions """
from allennlp.training.metrics.metric import Metric
from overrides import overrides
import torch


@Metric.register("mrr")
class MeanReciprocalRank(Metric):
    def __init__(self) -> None:
        self._sum = 0.0
        self._n = 0.0

    def __call__(
        self, predictions: torch.Tensor, labels: torch.Tensor, mask: torch.Tensor
    ) -> None:
        # Flatten
        labels = labels.view(-1)
        mask = mask.view(-1).float()
        predictions = predictions.view(labels.shape[0], -1)

        # MRR computation
        label_scores = predictions.gather(-1, labels.unsqueeze(-1))
        rank = predictions.ge(label_scores).sum(1).float()
        reciprocal_rank = 1 / rank
        self._sum += (reciprocal_rank * mask).sum().item()
        self._n += mask.sum().item()

    def get_metric(self, reset: bool = False) -> float:
        mrr = self._sum / (self._n + 1e-13)
        if reset:
            self.reset()
        return mrr

    @overrides
    def reset(self) -> None:
        self._sum = 0.0
        self._n = 0.0
