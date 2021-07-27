"""
TimeSeries Dataset Base Classes
-------------------------------
"""

from abc import ABC, abstractmethod
from torch.utils.data import Dataset
import numpy as np

from typing import Tuple, Optional
from ...logging import get_logger, raise_if_not
from ...timeseries import TimeSeries

logger = get_logger(__name__)


class TrainingDataset(ABC, Dataset):
    def __init__(self):
        """
        Super-class for all training datasets for torch models in Darts. These include

        * "PastCovariates" datasets (for PastCovariatesTorchModel): containing (past_target,
                                                                                past_covariates,
                                                                                future_target)
        * "FutureCovariates" datasets (for FutureCovariatesTorchModel): containing (past_target,
                                                                                    future_covariates,
                                                                                    future_target)
        * "DualCovariates" datasets (for DualCovariatesTorchModel): containing (past_target,
                                                                                historic_future_covariates,
                                                                                future_covariates,
                                                                                future_target)
        * "MixedCovariates" datasets (for MixedCovariatesTorchModel): containing (past_target,
                                                                                  past_covariates,
                                                                                  historic_future_covariates,
                                                                                  future_covariates,
                                                                                  future_target)
        * "SplitCovariates" datasets (for SplitCovariatesTorchModel): containing (past_target,
                                                                                  past_covariates,
                                                                                  future_covariates,
                                                                                  future_target)

        The covariates are optional and can be `None`.

        This is meant to be used for training (or validation), all data except `future_target` represents model
        inputs (`future_target` is the output the model are trained to predict).

        Darts `TorchForecastingModel`s can be fit from instances of `TrainingDataset` using the
        `fit_from_dataset()` method.

        `TrainingDataset` inherits from `Sequence`; meaning that the implementations have to
        provide the `__len__()` and `__getitem__()` methods.

        It contains `np.ndarray` (and not `TimeSeries`), because training requires the values only,
        and so we can get big performance gains when slicing by returning only numpy views of the data.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __getitem__(self, idx: int):
        pass


class PastCovariatesTrainingDataset(TrainingDataset, ABC):
    def __init__(self):
        """
        Abstract class for a PastCovariatesTorchModel training dataset. It contains 3-tuples of
        `(past_target, past_covariate, future_target)` `np.ndarray`.
        The covariates are optional and can be `None`.
        """
        super().__init__()

    @abstractmethod
    def __getitem__(self, idx: int) -> Tuple[np.ndarray, Optional[np.ndarray], np.ndarray]:
        pass


class FutureCovariatesTrainingDataset(TrainingDataset, ABC):
    def __init__(self):
        """
        Abstract class for a FutureCovariatesTorchModel training dataset. It contains 3-tuples of
        `(past_target, future_covariate, future_target)` `np.ndarray`.
        The covariates are optional and can be `None`.
        """
        super().__init__()

    @abstractmethod
    def __getitem__(self, idx: int) -> Tuple[np.ndarray, Optional[np.ndarray], np.ndarray]:
        pass


class DualCovariatesTrainingDataset(TrainingDataset, ABC):
    def __init__(self):
        """
        Abstract class for a DualCovariatesTorchModel training dataset. It contains 4-tuples of
        `(past_target, historic_future_covariates, future_covariates, future_target)` `np.ndarray`.
        The covariates are optional and can be `None`.
        """
        super().__init__()

    @abstractmethod
    def __getitem__(self, idx: int) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray], np.ndarray]:
        pass


class MixedCovariatesTrainingDataset(TrainingDataset, ABC):
    def __init__(self):
        """
        Abstract class for a MixedCovariatesTorchModel training dataset. It contains 5-tuples of
        `(past_target, past_covariates, historic_future_covariates, future_covariates, future_target)` `np.ndarray`.
        The covariates are optional and can be `None`.
        """
        super().__init__()

    @abstractmethod
    def __getitem__(self, idx: int) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray],
                                             Optional[np.ndarray], np.ndarray]:
        pass


class SplitCovariatesTrainingDataset(TrainingDataset, ABC):
    def __init__(self):
        """
        Abstract class for a SplitCovariatesTorchModel training dataset. It contains 4-tuples of
        `(past_target, past_covariates, future_covariates, future_target)` `np.ndarray`.
        The covariates are optional and can be `None`.
        """
        super().__init__()

    @abstractmethod
    def __getitem__(self, idx: int) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray], np.ndarray]:
        pass


def _get_matching_index(ts_target: TimeSeries,
                        ts_covariate: TimeSeries,
                        idx: int):
    """
    Given two overlapping series `ts_target` and `ts_covariate` and an index point of `ts_target`, returns the matching
    index point in `ts_covariate`, based on the ending times of the two series.
    The indexes are starting from the end of the series.

    This function is used to jointly slice target and covariate series in datasets. It supports both datetime and
    integer indexed series.

    Note: this function does not check if the matching index value is in `ts_covariate` or not.
    """
    raise_if_not(ts_target.freq == ts_covariate.freq,
                 'The dataset contains some target/covariates series pair that have incompatible '
                 'time axes (not the same "freq") and thus cannot be matched')

    # compute the number of steps the covariates are in advance w.r.t. the target:
    time_diff = int((ts_covariate.end_time() - ts_target.end_time()) / ts_target.freq)
    return idx + time_diff