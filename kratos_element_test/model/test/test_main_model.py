import unittest

from kratos_element_test.model.main_model import MainModel
from kratos_element_test.model.models import MohrCoulombOptions


class MainModelTest(unittest.TestCase):
    def test_running_a_linear_elastic_triaxial_simulation(self):
        model = MainModel(logger=lambda msg, level: None)

        material_parameters = [9e5, 0.3]

        model.run_simulation(
            "linear elastic model", None, 0, MohrCoulombOptions(), material_parameters
        )

        results = model.get_latest_results()
        self.assertIsNotNone(results)


if __name__ == "__main__":
    unittest.main()
