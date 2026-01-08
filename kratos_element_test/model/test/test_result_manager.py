import unittest
from typing import Dict

from parameterized import parameterized

from kratos_element_test.model.result_manager import ResultManager
from kratos_element_test.view.ui_constants import TRIAXIAL, DIRECT_SHEAR, CRS


class ResultManagerTest(unittest.TestCase):

    @parameterized.expand([TRIAXIAL, DIRECT_SHEAR, CRS])
    def test_results_are_empty_dictionary_initially(self, test_name):
        current_test_getter = lambda: test_name
        result_manager = ResultManager(current_test_getter)

        test_results = result_manager.get_results()
        self.assertIsInstance(test_results, Dict)
        self.assertEqual(len(test_results), 0)

    def test_results_can_be_set_and_retrieved(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)
        expected_results = {
            "values_variable_1": [1, 2, 3],
            "values_variable_2": [4, 5, 6],
        }

        result_manager.set_results(expected_results)

        self.assertDictEqual(result_manager.get_results(), expected_results)


if __name__ == "__main__":
    unittest.main()
