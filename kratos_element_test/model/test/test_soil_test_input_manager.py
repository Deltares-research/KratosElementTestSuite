import unittest

from kratos_element_test.model.soil_test_input_manager import SoilTestInputManager


class SoilTestInputManagerTest(unittest.TestCase):
    def test_construction_of_input_manager(self):
        input_manager = SoilTestInputManager()
        self.assertEqual(len(input_manager.input_data), 3)

    def test_max_strain_for_crs(self):
        input_manager = SoilTestInputManager()
        crs_inputs = input_manager.input_data.get("CRS")
        self.assertIsNotNone(crs_inputs)
        self.assertEqual(len(crs_inputs.strain_increments), 5)

        expected_max_strain = 0.0
        self.assertEqual(expected_max_strain, crs_inputs.maximum_strain)

    def test_total_number_of_steps_for_crs(self):
        input_manager = SoilTestInputManager()
        crs_inputs = input_manager.input_data.get("CRS")
        self.assertIsNotNone(crs_inputs)
        self.assertEqual(len(crs_inputs.strain_increments), 5)

        expected_number_of_steps = 500  # 5 increments * 100 steps each
        self.assertEqual(expected_number_of_steps, crs_inputs.number_of_steps)

    def test_total_duration_for_crs(self):
        input_manager = SoilTestInputManager()
        crs_inputs = input_manager.input_data.get("CRS")
        self.assertIsNotNone(crs_inputs)
        self.assertEqual(len(crs_inputs.strain_increments), 5)

        expected_duration = 5.0 * 3600  # 5 increments * 1.0 hour each
        self.assertEqual(expected_duration, crs_inputs.duration_in_seconds)

    def test_max_strain_for_crs_after_updates(self):
        input_manager = SoilTestInputManager()

        input_manager.set_crs_strain_increment(index=0, new_increment=0.02)
        input_manager.set_crs_strain_increment(index=1, new_increment=0.04)

        crs_inputs = input_manager.input_data.get("CRS")

        expected_max_strain = 0.06
        self.assertEqual(expected_max_strain, crs_inputs.maximum_strain)

    def test_duration_for_crs_after_updates(self):
        input_manager = SoilTestInputManager()

        input_manager.set_crs_duration(index=0, new_duration_in_hours=1.5)

        crs_inputs = input_manager.input_data.get("CRS")

        expected_duration = 5.5 * 3600
        self.assertEqual(expected_duration, crs_inputs.duration_in_seconds)

    def test_number_of_steps_for_crs_after_updates(self):
        input_manager = SoilTestInputManager()

        input_manager.set_crs_steps(index=0, new_steps=150)

        crs_inputs = input_manager.input_data.get("CRS")

        expected_number_of_steps = 550
        self.assertEqual(expected_number_of_steps, crs_inputs.number_of_steps)


if __name__ == "__main__":
    unittest.main()
