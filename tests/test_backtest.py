import unittest
import numpy as np
import pandas as pd
from market_signal_lab.backtest import simulate


class BacktestTests(unittest.TestCase):
    def prices(self):
        close = 100 + np.arange(400)*0.05 + 3*np.sin(np.arange(400)/5)
        return pd.DataFrame({"Close": close, "High": close+1, "Low": close-1},
                            index=pd.bdate_range("2020-01-01", periods=400))

    def test_future_prices_do_not_change_past(self):
        prices = self.prices()
        original, _ = simulate(prices, prices.index[220])
        prices.iloc[320:] *= 2
        changed, _ = simulate(prices, prices.index[220])
        pd.testing.assert_frame_equal(original.iloc[:100], changed.iloc[:100])

    def test_signal_delay_and_costs(self):
        prices = self.prices()
        frame, _ = simulate(prices, prices.index[220], cost=0.01)
        expected = frame.target.ffill().fillna(0).shift(2).fillna(0)
        pd.testing.assert_series_equal(frame.position, expected, check_names=False)
        self.assertGreater(frame.turnover.sum(), 0)
        np.testing.assert_allclose(frame.strategy_return,
                                   frame.position*frame.market_return-frame.turnover*0.01)
        self.assertEqual(frame.position.iloc[0], 0)

    def test_reject_missing_warmup(self):
        with self.assertRaises(ValueError):
            simulate(self.prices(), "2020-01-01")


if __name__ == "__main__":
    unittest.main()
