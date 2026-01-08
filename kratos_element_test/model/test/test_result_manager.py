import unittest
from typing import Dict

from parameterized import parameterized

from kratos_element_test.model.result_manager import ResultManager
from kratos_element_test.view.ui_constants import TRIAXIAL, DIRECT_SHEAR, CRS


class ResultManagerTest(unittest.TestCase):

    @parameterized.expand([TRIAXIAL, DIRECT_SHEAR, CRS])
    def test_results_are_empty_dictionary_initially(self, test_name):
        result_manager = ResultManager()

        test_results = result_manager.get_results(test_name)
        self.assertIsInstance(test_results, Dict)
        self.assertEqual(len(test_results), 0)

if __name__ == '__main__':
    unittest.main()
