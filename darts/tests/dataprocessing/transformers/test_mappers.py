import unittest
from numpy.lib.arraysetops import isin
import pandas as pd

from ....timeseries import TimeSeries
from darts.dataprocessing.transformers.mappers import Mapper, InvertibleMapper
from darts.utils.timeseries_generation import constant_timeseries, linear_timeseries


class MappersTestCase(unittest.TestCase):

    @staticmethod
    def func(x):
        return x + 10

    @staticmethod
    def inverse_func(x):
        return x - 10

    @staticmethod
    def ts_func(ts, x):
        return x - ts.month

    @staticmethod
    def inverse_ts_func(ts, x):
        return x + ts.month

    plus_ten = Mapper(func.__func__)
    plus_ten_invertible = InvertibleMapper(func.__func__, inverse_func.__func__)

    subtract_month = Mapper(ts_func.__func__)
    subtract_month_invertible = InvertibleMapper(ts_func.__func__, inverse_ts_func.__func__)

    lin_series = linear_timeseries(start_value=1, length=12, freq='MS', start_ts=pd.Timestamp('2000-01-01'), end_value=12)  # noqa: E501
    zeroes = constant_timeseries(value=0.0, length=12, freq='MS', start_ts=pd.Timestamp('2000-01-01'))
    tens = constant_timeseries(value=10.0, length=12, freq='MS', start_ts=pd.Timestamp('2000-01-01'))
    twenties = constant_timeseries(value=20.0, length=12, freq='MS', start_ts=pd.Timestamp('2000-01-01'))

    def test_mapper(self):

        test_cases = [
            (self.zeroes, self.tens),
            ([self.zeroes, self.tens], [self.tens, self.twenties])
        ]

        for to_transform, expected_output in test_cases:
            transformed = self.plus_ten.transform(to_transform)
            self.assertEqual(transformed, expected_output)

    def test_invertible_mapper(self):
        test_cases = [
            (self.zeroes),
            ([self.zeroes, self.tens])
        ]

        for data in test_cases:
            transformed = self.plus_ten_invertible.transform(data)
            back = self.plus_ten_invertible.inverse_transform(transformed)
            self.assertEqual(back, data)

    def test_mapper_with_timestamp(self):

        test_cases = [
            (self.lin_series, self.zeroes),
            ([self.lin_series, self.lin_series], [self.zeroes, self.zeroes])
        ]

        for to_transform, expected_output in test_cases:
            transformed = self.subtract_month.transform(to_transform)
            if isinstance(to_transform, list):
                tmp_t = []
                tmp_o = []
                for t, o in zip(transformed, expected_output):
                    o = o.with_column_renamed(o.components[0], t.components[0])
                    tmp_t.append(t)
                    tmp_o.append(o)
                transformed = tmp_t
                expected_output = tmp_o
            else:
                expected_output = expected_output.with_column_renamed(expected_output.components[0], transformed.components[0])
            self.assertEqual(transformed, expected_output)

    def test_invertible_mapper_with_timestamp(self):

        test_cases = [
            (self.lin_series),
            ([self.lin_series, self.lin_series])
        ]

        for data in test_cases:
            transformed = self.subtract_month_invertible.transform(data)
            back = self.subtract_month_invertible.inverse_transform(transformed)
            self.assertEqual(back, data)
