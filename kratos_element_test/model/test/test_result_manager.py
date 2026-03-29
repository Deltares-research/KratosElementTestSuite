import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

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
            "values_variable_1": [1.0, 2.0, 3.0],
            "values_variable_2": [4.0, 5.0, 6.0],
        }

        result_manager.set_results_of_active_test_type(expected_results)

        results = result_manager.get_results_of_active_test_type()
        assert results is not None
        self.assertDictEqual(results, expected_results)

    def test_workflow_with_results_for_multiple_test_types(self):
        current_test_type = TRIAXIAL
        current_test_getter = lambda: current_test_type
        result_manager = ResultManager(current_test_getter)
        expected_triaxial_results = {
            "values_variable_1": [1.0, 2.0, 3.0],
            "values_variable_2": [4.0, 5.0, 6.0],
        }
        result_manager.set_results_of_active_test_type(expected_triaxial_results)

        current_test_type = CRS
        expected_crs_data = {"some_other_data": [7.0, 8.0, 9.0]}
        result_manager.set_results_of_active_test_type(expected_crs_data)
        results = result_manager.get_results_of_active_test_type()
        assert results is not None
        self.assertDictEqual(results, expected_crs_data)

        current_test_type = TRIAXIAL
        results = result_manager.get_results_of_active_test_type()
        assert results is not None
        self.assertDictEqual(results, expected_triaxial_results)

    def test_clear_results(self):
        # Arrange
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)
        expected_results = {
            "values_variable_1": [1.0, 2.0, 3.0],
            "values_variable_2": [4.0, 5.0, 6.0],
        }
        result_manager.set_results_of_active_test_type(expected_results)

        # Act
        result_manager.clear_results()

        # Assert
        self.assertIsNone(result_manager.get_results_of_active_test_type())

    def test_result_manager_has_empty_experimental_results(self):
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
            result_manager.import_lab_results_dict(cast(Any, None))

        with self.assertRaises(ValueError):
            result_manager.import_lab_results_dict({})

        with self.assertRaises(ValueError):
            result_manager.import_lab_results_dict(cast(Any, "not a dict"))

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

    def test_import_csv_lab_results_requires_active_test_selection(self):
        current_test_getter = lambda: ""
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "triaxial_lab.csv"
            csv_file.write_text(
                "yy_strain,sigma1,sigma3,vol_strain,p,q\n"
                "0.0,-100,-100,0.0,-100,0\n"
                "-0.1,-250,-100,-0.01,-150,150\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as context:
                result_manager.import_csv_lab_results(csv_file)

            self.assertIn("No active test selected", str(context.exception))

    def test_import_csv_lab_results_uses_active_test_type_when_not_provided(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "triaxial_lab.csv"
            csv_file.write_text(
                "yy_strain,sigma1,sigma3,vol_strain,p,q\n"
                "0.0,-100,-100,0.0,-100,0\n"
                "-0.1,-250,-100,-0.01,-150,150\n",
                encoding="utf-8",
            )

            imported_test_type = result_manager.import_csv_lab_results(csv_file)

        self.assertEqual(imported_test_type, "triaxial")

        imported = result_manager.get_experimental_results()
        self.assertDictEqual(
            {
                "p'": [-100.0, -150.0],
                "q": [0.0, 150.0],
                "sigma1_sigma3_diff": [0.0, 150.0],
                "sigma_1": [-100.0, -250.0],
                "sigma_3": [-100.0, -100.0],
            },
            imported,
        )

    def test_import_csv_lab_results_with_test_type_column_routes_data_per_test(self):
        # Use a mutable object for current_test_type
        current_test_type = [TRIAXIAL]
        current_test_getter = lambda: current_test_type[0]
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "multi_test_lab.csv"
            csv_file.write_text(
                "test_type,yy_strain,sigma1_sigma3_diff,shear_strain_xy,shear_stress_xy\n"
                "Triaxial,0.0,0.0,,\n"
                "Triaxial,-0.1,120.0,,\n"
                "Direct Simple Shear,,,0.0,0.0\n"
                "Direct Simple Shear,,,0.05,40.0\n",
                encoding="utf-8",
            )

            result_manager.import_csv_lab_results(csv_file)

        # Check Triaxial results
        current_test_type[0] = TRIAXIAL
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "Vertical Strain": [0.0, -0.1],
                "sigma1_sigma3_diff": [0.0, 120.0],
            },
        )

        # Check Direct Simple Shear results
        current_test_type[0] = DIRECT_SHEAR
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {},
        )

    def test_import_csv_lab_results_preserves_other_tests_data(self):
        current_test_type = TRIAXIAL
        current_test_getter = lambda: current_test_type
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            triaxial_csv = Path(tmp_dir) / "triaxial_lab.csv"
            triaxial_csv.write_text(
                "yy_strain,sigma1_sigma3_diff\n" "0.0,0.0\n" "-0.1,120.0\n",
                encoding="utf-8",
            )

            dss_csv = Path(tmp_dir) / "dss_lab.csv"
            dss_csv.write_text(
                "shear_strain_xy,shear_stress_xy\n" "0.0,0.0\n" "0.05,40.0\n",
                encoding="utf-8",
            )

            result_manager.import_csv_lab_results(triaxial_csv)

            current_test_type = DIRECT_SHEAR
            result_manager.import_csv_lab_results(dss_csv)

        current_test_type = TRIAXIAL
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "sigma1_sigma3_diff": [0.0, 120.0],
            },
        )

        current_test_type = DIRECT_SHEAR
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "shear_strain_xy": [0.0, 0.05],
                "shear_stress_xy": [0.0, 40.0],
            },
        )

    def test_import_csv_lab_results_supports_cp1252_encoding(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "cp1252_lab.csv"
            csv_content = (
                "yy_strain,sigma1,sigma3,comment\n"
                "0.0,-100,-100,Þ\n"
                "-0.1,-250,-100,Þ\n"
            )
            csv_file.write_bytes(csv_content.encode("cp1252"))

            result_manager.import_csv_lab_results(csv_file)

        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "sigma_1": [-100.0, -250.0],
                "sigma_3": [-100.0, -100.0],
                "sigma1_sigma3_diff": [0.0, 150.0],
            },
        )

    def test_import_csv_lab_results_rejects_excel_workbook_extension(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            excel_file = Path(tmp_dir) / "lab_results.xlsx"
            excel_file.write_bytes(b"PK\x03\x04")

            with self.assertRaises(ValueError) as context:
                result_manager.import_csv_lab_results(excel_file)

        self.assertIn("Excel workbook", str(context.exception))

    def test_import_csv_lab_results_supports_semicolon_delimiter(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "semicolon_delimited.csv"
            csv_content = (
                "yy_strain;sigma1;sigma3;vol_strain;p;q\n"
                "0.0;-100;-100;0.0;-100;0\n"
                "-0.1;-250;-100;-0.01;-150;150\n"
            )
            csv_file.write_text(csv_content, encoding="utf-8")

            result_manager.import_csv_lab_results(csv_file)

        imported = result_manager.get_experimental_results()
        self.assertDictEqual(
            {
                "p'": [-100.0, -150.0],
                "q": [0.0, 150.0],
                "sigma1_sigma3_diff": [0.0, 150.0],
                "sigma_1": [-100.0, -250.0],
                "sigma_3": [-100.0, -100.0],
            },
            imported,
        )

    def test_import_csv_lab_results_supports_common_lab_header_labels(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "lab_headers.csv"
            csv_content = (
                "Axial Strain (%);Deviator Stress q (kPa);Mean Effective Stress p' (kPa)\n"
                "0.0;0.0;-100\n"
                "-0.1;150.0;-150\n"
            )
            csv_file.write_text(csv_content, encoding="utf-8")

            result_manager.import_csv_lab_results(csv_file)

        imported = result_manager.get_experimental_results()
        self.assertDictEqual(
            imported,
            {
                "q": [0.0, 150.0],
                "p'": [-100.0, -150.0],
                "sigma1_sigma3_diff": [0.0, 150.0],
            },
        )

    def test_import_csv_lab_results_supports_user_column_mapping(self):
        current_test_getter = lambda: TRIAXIAL
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "manual_mapping.csv"
            csv_content = "sigma;epsilon\n" "0.0;0.0\n" "120.0;-0.1\n"
            csv_file.write_text(csv_content, encoding="utf-8")

            result_manager.import_csv_lab_results(
                csv_file,
                column_mapping={
                    "q": "sigma",
                    "yy_strain": "epsilon",
                },
            )

        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {"q": [0.0, 120.0], "sigma1_sigma3_diff": [0.0, 120.0]},
        )

    def test_import_csv_lab_results_keeps_multi_model_data_without_test_type_column(
        self,
    ):
        # When importing without a test_type column, data is only imported to the active test
        current_test_type = TRIAXIAL
        current_test_getter = lambda: current_test_type
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "triaxial_crs_combined.csv"
            csv_content = (
                "yy_strain,vol_strain,sigma1,sigma3,sigma_xx,sigma_yy,time_hours\n"
                "0.0,0.0,-100,-100,-80,-100,0\n"
                "-0.1,-0.02,-250,-100,-120,-180,12\n"
            )
            csv_file.write_text(csv_content, encoding="utf-8")

            result_manager.import_csv_lab_results(csv_file)

        # Data is only imported to the active test (TRIAXIAL)
        current_test_type = TRIAXIAL
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "sigma_1": [-100.0, -250.0],
                "sigma_3": [-100.0, -100.0],
                "sigma1_sigma3_diff": [0.0, 150.0],
            },
        )

        # CRS should not have any data since it wasn't the active test
        current_test_type = CRS
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {},
        )

        current_test_type = DIRECT_SHEAR
        self.assertDictEqual(result_manager.get_experimental_results(), {})

    def test_import_csv_lab_results_with_manual_mapping_imports_only_to_active_test_type(self):
        # When mapping columns manually, data is only imported to the active test
        current_test_type = TRIAXIAL
        current_test_getter = lambda: current_test_type
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "manual_multi_mapping.csv"
            csv_content = (
                "axial,delta_sigma,horizontal,vertical,time\n"
                "0.0,0.0,-80,-100,0\n"
                "-0.1,150,-120,-180,10\n"
            )
            csv_file.write_text(csv_content, encoding="utf-8")

            result_manager.import_csv_lab_results(
                csv_file,
                column_mapping={
                    "yy_strain": "axial",
                    "sigma1_sigma3_diff": "delta_sigma",
                    "sigma_xx": "horizontal",
                    "sigma_yy": "vertical",
                    "time_steps": "time",
                },
            )

        # Data is only imported to the active test (TRIAXIAL)
        current_test_type = TRIAXIAL
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "sigma1_sigma3_diff": [0.0, 150.0],
            },
        )

        # CRS should not have any data since it wasn't the active test
        current_test_type = CRS
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {},
        )

        current_test_type = DIRECT_SHEAR
        self.assertDictEqual(result_manager.get_experimental_results(), {})

    def test_import_csv_lab_results_imports_to_explicit_crs_target(self):
        current_test_type = TRIAXIAL
        current_test_getter = lambda: current_test_type
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "crs_mapping.csv"
            csv_content = "sigma;epsilon\n" "100.0;200.0\n" "110.0;220.0\n"
            csv_file.write_text(csv_content, encoding="utf-8")

            imported_test_type = result_manager.import_csv_lab_results(
                csv_file,
                column_mapping={
                    "sigma_xx": "sigma",
                    "sigma_yy": "epsilon",
                },
                target_test_type="crs",
            )

        self.assertEqual(imported_test_type, "crs")

        current_test_type = TRIAXIAL
        self.assertDictEqual(result_manager.get_experimental_results(), {})

        current_test_type = CRS
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "sigma_xx": [100.0, 110.0],
                "sigma_yy": [200.0, 220.0],
            },
        )

    def test_import_csv_lab_results_shared_columns_only_in_active_test(self):
        """Shared columns (p' and q) are only imported to the active test,
        not to all compatible test types."""
        current_test_type = TRIAXIAL
        current_test_getter = lambda: current_test_type
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "pq_only.csv"
            csv_file.write_text(
                "p,q\n" "-100,0\n" "-150,150\n",
                encoding="utf-8",
            )

            result_manager.import_csv_lab_results(csv_file)

        # _compute_missing_sigma_diff derives sigma1_sigma3_diff from q when
        # sigma_1 and sigma_3 are absent, so it is present in the stored results.
        expected = {
            "p'": [-100.0, -150.0],
            "q": [0.0, 150.0],
            "sigma1_sigma3_diff": [0.0, 150.0],
        }

        # Data is only in the active test (TRIAXIAL)
        current_test_type = TRIAXIAL
        self.assertDictEqual(result_manager.get_experimental_results(), expected)

        # Other test types should not have the data
        current_test_type = DIRECT_SHEAR
        self.assertDictEqual(result_manager.get_experimental_results(), {})

        current_test_type = CRS
        self.assertDictEqual(result_manager.get_experimental_results(), {})


if __name__ == "__main__":
    unittest.main()
