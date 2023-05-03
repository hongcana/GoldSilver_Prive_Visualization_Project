from PriceDashBoard.data_preprocess import data_preprocess
import unittest
class data_preprocess_test(unittest.TestCase):
    def test_add(self):
        expected = {"material_name_id":1.0,"price":1995.4,"upper_20":0.0,"upper_60":1.0,"regular_array":1.0}
        output = data_preprocess(1)

        self.assertEqual(output, expected)