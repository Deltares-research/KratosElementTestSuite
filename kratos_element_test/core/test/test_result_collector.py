import os
import unittest
from pathlib import Path

from kratos_element_test.core.pipeline.result_collector import ResultCollector


class ResultCollectorTest(unittest.TestCase):
    def test_all_results_are_present(self):
        file_path = Path(os.path.dirname(__file__))
        test_path = file_path / "output.post.res"
        collector = ResultCollector([test_path], material_parameters=[], cohesion_phi_indices=None)
        results = collector.collect_results()
        self.assertIn("yy_strain", results)
        self.assertIn("vol_strain", results)
        self.assertIn("sigma1", results)
        self.assertIn("sigma3", results)
        self.assertIn("shear_xy", results)
        self.assertIn("shear_strain_xy", results)
        self.assertIn("mean_stress", results)
        self.assertIn("von_mises", results)
        self.assertIn("cohesion", results)
        self.assertIn("phi", results)
        self.assertIn("sigma_xx", results)
        self.assertIn("sigma_yy", results)
        self.assertIn("time_steps", results)


if __name__ == "__main__":
    unittest.main()
