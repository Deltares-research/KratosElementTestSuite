import unittest

from kratos_element_test.model.main_model import MainModel
from kratos_element_test.model.material_inputs import MohrCoulombOptions


class MainModelTest(unittest.TestCase):
    def test_running_a_linear_elastic_triaxial_simulation(self):
        model = MainModel(logger=lambda msg, level: None)

        model.get_material_input_manager().set_current_material_type("linear_elastic")
        model.get_material_input_manager().update_material_parameter_of_current_type(
            "YOUNG_MODULUS", 9e5
        )
        model.get_material_input_manager().update_material_parameter_of_current_type(
            "POISSON_RATIO", 0.3
        )

        model.run_simulation(
            model_name="linear elastic model",
            dll_path=None,
            udsm_number=0,
            mohr_coulomb_options=MohrCoulombOptions(),
            material_parameters=[],
        )

        results = model.get_latest_results()
        self.assertIsNotNone(results)
        self.assertTrue(len(results) > 0)


if __name__ == "__main__":
    unittest.main()
