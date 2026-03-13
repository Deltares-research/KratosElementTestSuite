import unittest
import numpy as np

from kratos_element_test.model.core_utils import (
    last_float,
    gamma_from_shear_strain_xy,
    compute_mohr_circle_xy,
)


class CoreUtilsTest(unittest.TestCase):
    def test_last_float_returns_last_element_for_list(self):
        self.assertEqual(last_float([1.0, 2.0, 3.0]), 3.0)

    def test_gamma_from_shear_strain_xy_returns_absolute_doubled_values(self):
        self.assertEqual(
            gamma_from_shear_strain_xy([0.0, -0.1, 0.2]),
            [0.0, 0.2, 0.4],
        )

    def test_compute_mohr_circle_xy_returns_none_for_missing_input(self):
        self.assertIsNone(compute_mohr_circle_xy(None, [1.0, 2.0]))

    def test_compute_mohr_circle_xy_returns_correct_coordinates(self):
        sigma_1 = [100.0, 150.0, 200.0]
        sigma_3 = [50.0, 75.0, 100.0]

        sigma, tau = compute_mohr_circle_xy(sigma_1, sigma_3, n_points=3)

        expected_sigma = [200.0, 150.0, 100.0]
        expected_tau = [0.0, -50.0, 0.0]

        np.testing.assert_array_almost_equal(sigma, expected_sigma)
        np.testing.assert_array_almost_equal(tau, expected_tau)


if __name__ == "__main__":
    unittest.main()
