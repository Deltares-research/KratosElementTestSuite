import unittest

from parameterized import parameterized

from kratos_element_test.model.soil_test_input_manager import SoilTestInputManager
from kratos_element_test.view.ui_constants import TRIAXIAL, DIRECT_SHEAR


class SoilTestInputManagerTest(unittest.TestCase):
    def setUp(self):
        self.input_manager = SoilTestInputManager()

    def test_default_crs_input(self):
        crs_inputs = self.input_manager.input_data.get("CRS")
        self.assertIsNotNone(crs_inputs)
        self.assertEqual(len(crs_inputs.strain_increments), 5)

    def test_total_number_of_steps_for_crs(self):
        crs_inputs = self.input_manager.input_data.get("CRS")

        expected_number_of_steps = 500  # 5 increments * 100 steps each by default
        self.assertEqual(expected_number_of_steps, crs_inputs.number_of_steps)

    def test_total_duration_for_crs(self):
        crs_inputs = self.input_manager.input_data.get("CRS")

        expected_duration = 5.0 * 3600  # 5 increments * 1.0 hour each by default
        self.assertEqual(expected_duration, crs_inputs.duration_in_seconds)

    def test_max_strain_for_crs_is_sum_of_stain_increments_after_updates(self):
        self.input_manager.set_crs_strain_increment(index=0, new_increment=0.02)
        self.input_manager.set_crs_strain_increment(index=1, new_increment=0.04)

        crs_inputs = self.input_manager.input_data.get("CRS")

        expected_max_strain = 0.06
        self.assertEqual(expected_max_strain, crs_inputs.maximum_strain)

    def test_duration_for_crs_after_updates(self):
        self.input_manager.set_crs_duration(index=0, new_duration_in_hours=1.5)

        crs_inputs = self.input_manager.input_data.get("CRS")

        expected_duration = 5.5 * 3600
        self.assertEqual(expected_duration, crs_inputs.duration_in_seconds)

    def test_number_of_steps_for_crs_after_updates(self):
        self.input_manager.set_crs_steps(index=0, new_steps=150)

        crs_inputs = self.input_manager.input_data.get("CRS")

        expected_number_of_steps = 550
        self.assertEqual(expected_number_of_steps, crs_inputs.number_of_steps)

    def test_adding_crs_strain_increment(self):
        initial_count = len(self.input_manager.input_data.get("CRS").strain_increments)
        self.input_manager.add_strain_increment()
        new_count = len(self.input_manager.input_data.get("CRS").strain_increments)

        self.assertEqual(initial_count + 1, new_count)

    def test_removing_strain_increment(self):
        initial_count = len(self.input_manager.input_data.get("CRS").strain_increments)
        self.input_manager.remove_last_crs_strain_increment()
        new_count = len(self.input_manager.input_data.get("CRS").strain_increments)

        self.assertEqual(initial_count - 1, new_count)

    def test_removing_last_strain_increment_is_not_possible(self):
        initial_count = len(self.input_manager.input_data.get("CRS").strain_increments)

        for _ in range(initial_count):
            self.input_manager.remove_last_crs_strain_increment()

        new_count = len(self.input_manager.input_data.get("CRS").strain_increments)
        self.assertEqual(1, new_count)

    @parameterized.expand([TRIAXIAL, DIRECT_SHEAR])
    def test_update_duration(self, test_type):
        self.input_manager.update_duration(2.5, test_type)
        updated = self.input_manager.input_data[test_type].duration_in_seconds
        self.assertEqual(updated, 2.5)

    @parameterized.expand([TRIAXIAL, DIRECT_SHEAR])
    def test_update_num_steps(self, test_type):
        self.input_manager.update_num_steps(250, test_type)
        updated = self.input_manager.input_data[test_type].number_of_steps
        self.assertEqual(updated, 250)

    @parameterized.expand([TRIAXIAL, DIRECT_SHEAR])
    def test_update_max_strain(self, test_type):
        self.input_manager.update_max_strain(15.0, test_type)
        updated = self.input_manager.input_data[test_type].maximum_strain
        self.assertEqual(updated, 15.0)

    @parameterized.expand([TRIAXIAL, DIRECT_SHEAR])
    def test_update_init_pressure(self, test_type):
        self.input_manager.update_init_pressure(250.0, test_type)
        updated = self.input_manager.input_data[
            test_type
        ].initial_effective_cell_pressure
        self.assertEqual(updated, 250.0)

    def test_get_current_default_inputs(self):
        inputs = self.input_manager.get_current_test_inputs()
        self.assertIsNotNone(inputs)
        self.assertEqual(inputs.maximum_strain, 20.0)
        self.assertEqual(inputs.duration_in_seconds, 1.0)
        self.assertEqual(inputs.number_of_steps, 100)

    def test_get_current_default_inputs_for_crs(self):
        self.input_manager.set_current_test_type("CRS")
        inputs = self.input_manager.get_current_test_inputs()
        self.assertIsNotNone(inputs)
        self.assertEqual(inputs.maximum_strain, 0.0)
        self.assertEqual(inputs.duration_in_seconds, 18000.0)
        self.assertEqual(inputs.number_of_steps, 500)

    def test_setting_non_existent_test_type_throws(self):
        self.assertRaises(
            ValueError, lambda: self.input_manager.set_current_test_type("Non-existent")
        )


if __name__ == "__main__":
    unittest.main()
