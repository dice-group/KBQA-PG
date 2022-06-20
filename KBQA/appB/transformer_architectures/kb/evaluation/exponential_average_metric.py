from typing import Union

from allennlp.training.metrics.metric import Metric
from overrides import overrides


@Metric.register("ema")
class ExponentialMovingAverage(Metric):
    """
    Keep an exponentially weighted moving average.
    alpha is the decay constant. Alpha = 1 means just keep the most recent value.
    alpha = 0.5 will have almost no contribution from 10 time steps ago.
    """

    def __init__(self, alpha: float = 0.5) -> None:
        self.alpha = alpha
        self.reset()
        self._ema: Union[None, float] = None

    @overrides
    def __call__(self, value: float) -> None:
        """
        Parameters
        ----------
        value : ``float``
            The value to average.
        """
        if self._ema is None:
            # first observation
            self._ema = value
        else:
            self._ema = self.alpha * value + (1.0 - self.alpha) * self._ema

    @overrides
    def get_metric(self, reset: bool = False) -> float:
        """
        Returns
        -------
        The average of all values that were passed to ``__call__``.
        """
        if self._ema is None:
            ret = 0.0
        else:
            ret = self._ema

        if reset:
            self.reset()

        return ret

    @overrides
    def reset(self) -> None:
        self._ema = None
