import unittest

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

    def test_result_manager_has_empty_experimental_results(self) -> bool:
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        experimental = result_manager.get_experimental_results()

        self.assertIsInstance(experimental, dict)

    def test_experimental_results_can_be_set_and_retrieved(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        expected_experimental_results = {
            "yy_strain": [0.0, -0.02],
            "vol_strain": [0.0, -8.724e-3],
        }

        result_manager.set_experimental_results_for_test_type(
            TRIAXIAL, expected_experimental_results
        )

        self.assertDictEqual(
            result_manager.get_experimental_results(), expected_experimental_results
        )

    def test_import_lab_results_dict_sets_results_for_active_test(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        experimental_by_test = {
            "triaxial": {
                "yy_strain": [0.0, -0.02],
                "vol_strain": [0.0, -0.01],
            }
        }

        result_manager.import_lab_results_dict(experimental_by_test)

        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "yy_strain": [0.0, -0.02],
                "vol_strain": [0.0, -0.01],
            },
        )

    def test_import_lab_results_dict_removes_stale_results_for_missing_test_types(self):
        current_test_type = TRIAXIAL
        current_test_getter = lambda: current_test_type
        result_manager = ResultManager(current_test_getter)

        result_manager.set_experimental_results_for_test_type(
            TRIAXIAL, {"yy_strain": [0.0, -0.02]}
        )
        result_manager.set_experimental_results_for_test_type(
            CRS, {"sigma_yy": [0.0, -100.0]}
        )

        experimental_by_test = {"crs": {"sigma_yy": [0.0, -200.0]}}

        result_manager.import_lab_results_dict(experimental_by_test)

        current_test_type = TRIAXIAL
        self.assertDictEqual(result_manager.get_experimental_results(), {})

        current_test_type = CRS
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {"sigma_yy": [0.0, -200.0]},
        )

    def test_import_lab_results_dict_raises_for_invalid_input(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        with self.assertRaises(ValueError):
            result_manager.import_lab_results_dict(None)

        with self.assertRaises(ValueError):
            result_manager.import_lab_results_dict({})

        with self.assertRaises(ValueError):
            result_manager.import_lab_results_dict("not a dict")

    def test_import_lab_results_dict_ignores_invalid_entries(self):
        current_test_type = DIRECT_SHEAR
        current_test_getter = lambda: current_test_type
        result_manager = ResultManager(current_test_getter)

        experimental_by_test = {
            123: {"yy_strain": [0.0]},
            "triaxial": {},
            "direct_shear": {"shear_strain_xy": [0.0, 0.1]},
        }

        result_manager.import_lab_results_dict(experimental_by_test)

        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {"shear_strain_xy": [0.0, 0.1]},
        )

    def test_import_experimental_results_maps_type_name_to_storage_key(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        experimental_by_test = {"triaxial": {"yy_strain": [0.0, -0.02]}}

        result_manager.import_lab_results_dict(experimental_by_test)

        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {"yy_strain": [0.0, -0.02]},
        )


if __name__ == "__main__":
    unittest.main()
