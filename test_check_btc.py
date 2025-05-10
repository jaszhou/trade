import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from day_trade import check_btc_price

class TestCheckBTCPrice(unittest.TestCase):
    @patch('day_trade.client.get_klines')
    def test_check_btc_price(self, mock_get_klines):
        # Table-Driven Test Cases
        test_cases = [
            {
                "name": "Close price is greater than open price",
                "mock_data": [
                    [1633046400000, "40000", "41000", "39000", "40500", "1000", 0],
                    [1633132800000, "40500", "42000", "40000", "41000", "1200", 0]
                ],
                "expected_result": True
            },
            {
                "name": "Close price is less than open price",
                "mock_data": [
                    [1633046400000, "40000", "41000", "39000", "40500", "1000", 0],
                    [1633132800000, "41000", "42000", "40000", "40500", "1200", 0]
                ],
                "expected_result": False
            },
            {
                "name": "Close price is equal to open price",
                "mock_data": [
                    [1633046400000, "40000", "41000", "39000", "40500", "1000", 0],
                    [1633132800000, "40500", "42000", "40000", "40500", "1200", 0]
                ],
                "expected_result": False
            }
        ]

        for case in test_cases:
            with self.subTest(case["name"]):
                # Mock the API response
                mock_get_klines.return_value = case["mock_data"]

                # Run the function
                result = check_btc_price()

                # Assert the result
                self.assertEqual(result, case["expected_result"])

if __name__ == '__main__':
    unittest.main()
