import unittest

from kratos_element_test.model.main_model import MainModel
from kratos_element_test.model.models import MohrCoulombOptions


class MainModelTest(unittest.TestCase):
    def test_running_a_linear_elastic_triaxial_simulation(self):
        model = MainModel(logger=lambda msg, level: None)

        youngs_modulus = 9e5
        poisson_ratio = 0.3
        model.run_simulation(
            model_name="linear elastic model",
            dll_path=None,
            udsm_number=0,
            mohr_coulomb_options=MohrCoulombOptions(),
            material_parameters=[youngs_modulus, poisson_ratio],
        )

        results = model.get_latest_results()
        self.assertIsNotNone(results)


if __name__ == "__main__":
    unittest.main()
