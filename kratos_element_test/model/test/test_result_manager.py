import unittest
from typing import Dict

from parameterized import parameterized

from kratos_element_test.model.result_manager import ResultManager
from kratos_element_test.view.ui_constants import TRIAXIAL, DIRECT_SHEAR, CRS


class ResultManagerTest(unittest.TestCase):

    @parameterized.expand([TRIAXIAL, DIRECT_SHEAR, CRS])
    def test_results_are_none_initially(self, test_name):
        current_test_getter = lambda: test_name
        result_manager = ResultManager(current_test_getter)

        test_results = result_manager.get_results_of_active_test_type()
        self.assertIsNone(test_results)

    def test_results_can_be_set_and_retrieved(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)
        expected_results = {
            "values_variable_1": [1, 2, 3],
            "values_variable_2": [4, 5, 6],
        }

        result_manager.set_results_of_active_test_type(expected_results)

        self.assertDictEqual(
            result_manager.get_results_of_active_test_type(), expected_results
        )

    def test_workflow_with_results_for_multiple_test_types(self):
        current_test_type = TRIAXIAL
        current_test_getter = lambda: current_test_type
        result_manager = ResultManager(current_test_getter)
        expected_triaxial_results = {
            "values_variable_1": [1, 2, 3],
            "values_variable_2": [4, 5, 6],
        }
        result_manager.set_results_of_active_test_type(expected_triaxial_results)

        current_test_type = CRS
        expected_crs_data = {"some_other_data": [7, 8, 9]}
        result_manager.set_results_of_active_test_type(expected_crs_data)
        self.assertDictEqual(
            result_manager.get_results_of_active_test_type(), expected_crs_data
        )

        current_test_type = TRIAXIAL
        self.assertDictEqual(
            result_manager.get_results_of_active_test_type(), expected_triaxial_results
        )

    def test_clear_results(self):
        # Arrange
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)
        expected_results = {
            "values_variable_1": [1, 2, 3],
            "values_variable_2": [4, 5, 6],
        }
        result_manager.set_results_of_active_test_type(expected_results)

        # Act
        result_manager.clear_results()

        # Assert
        self.assertIsNone(result_manager.get_results_of_active_test_type())


if __name__ == "__main__":
    unittest.main()
