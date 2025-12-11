import os
import unittest
from pathlib import Path
import numpy as np
from parameterized import parameterized

from kratos_element_test.core.pipeline.result_collector import ResultCollector


class ResultCollectorTest(unittest.TestCase):
    @parameterized.expand(
        [
            ["yy_strain", [0.0, -0.05, -0.1, -0.15, -0.2]],
            ["vol_strain", [0.0, -0.02, -0.04, -0.06, -0.08]],
            ["sigma1", [-100.0, -45100.0, -90100, -135100, -180100]],
            ["sigma3", [-100.0, -100.0, -100.0, -100.0, -100.0]],
            ["shear_xy", [0.0, 0.0, 0.0, 0.0, 0.0]],
            ["shear_strain_xy", [0.0, 0.0, 0.0, 0.0, 0.0]],
            ["mean_stress", [-100, -15100, -30100, -45100, -60100]],
            ["von_mises", [0.0, 45000, 90000, 135000, 180000]],
            ["cohesion", [3.0]],
            ["phi", [4.0]],
            ["sigma_xx", [-100.0, -100.0, -100.0, -100.0, -100.0]],
            ["sigma_yy", [-100.0, -45100.0, -90100, -135100, -180100]],
            [
                "time_steps", # in hours, hence the division by 3600
                [0.2 / 3600, 0.4 / 3600, 0.6 / 3600, 0.8 / 3600, 1.0 / 3600],
            ],
        ]
    )
    def test_collected_values(self, variable_name, expected_values):
        file_path = Path(os.path.dirname(__file__))
        test_path = file_path / "output.post.res"
        collector = ResultCollector(
            [test_path],
            material_parameters=[1.0, 2.0, 3.0, 4.0],
            cohesion_phi_indices=(3, 4),
        )
        results = collector.collect_results()
        np.testing.assert_array_almost_equal(results[variable_name], expected_values)

    def test_collector_does_not_throw_when_result_file_does_not_exist(self):
        collector = ResultCollector(
            [Path("non_existent_file.res")],
            material_parameters=[1.0, 2.0, 3.0, 4.0],
            cohesion_phi_indices=(3, 4),
        )
        try:
            results = collector.collect_results()
            self.assertIsInstance(results, dict)
        except Exception as e:
            self.fail(f"collect_results raised an exception unexpectedly: {e}")

    def test_c_phi_are_none_when_indices_are_not_defined(self):
        file_path = Path(os.path.dirname(__file__))
        test_path = file_path / "output.post.res"
        collector = ResultCollector(
            [test_path],
            material_parameters=[1.0, 2.0, 3.0, 4.0],
            cohesion_phi_indices=(),
        )

        results = collector.collect_results()
        self.assertTrue(results["cohesion"] is None)
        self.assertTrue(results["phi"] is None)


if __name__ == "__main__":
    unittest.main()
