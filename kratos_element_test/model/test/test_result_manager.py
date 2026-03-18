import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

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

            result_manager.import_csv_lab_results(csv_file)

        imported = result_manager.get_experimental_results()
        self.assertDictEqual(
            imported,
            {
                "yy_strain": [0.0, -0.1],
                "sigma_1": [-100.0, -250.0],
                "sigma_3": [-100.0, -100.0],
                "vol_strain": [0.0, -0.01],
                "p'": [-100.0, -150.0],
                "q": [0.0, 150.0],
                "sigma1_sigma3_diff": [0.0, 150.0],
            },
        )

    def test_import_csv_lab_results_with_test_type_column_routes_data_per_test(self):
        current_test_type = TRIAXIAL
        current_test_getter = lambda: current_test_type
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

        current_test_type = TRIAXIAL
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "yy_strain": [0.0, -0.1],
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
                "yy_strain": [0.0, -0.1],
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
            imported,
            {
                "yy_strain": [0.0, -0.1],
                "sigma_1": [-100.0, -250.0],
                "sigma_3": [-100.0, -100.0],
                "vol_strain": [0.0, -0.01],
                "p'": [-100.0, -150.0],
                "q": [0.0, 150.0],
                "sigma1_sigma3_diff": [0.0, 150.0],
            },
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
                "yy_strain": [0.0, -0.1],
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
            csv_content = (
                "sigma;epsilon\n"
                "0.0;0.0\n"
                "120.0;-0.1\n"
            )
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
            {
                "q": [0.0, 120.0],
                "yy_strain": [0.0, -0.1],
                "sigma1_sigma3_diff": [0.0, 120.0],
            },
        )

    def test_import_csv_lab_results_keeps_multi_model_data_without_test_type_column(self):
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

        current_test_type = TRIAXIAL
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "yy_strain": [0.0, -0.1],
                "vol_strain": [0.0, -0.02],
                "sigma_1": [-100.0, -250.0],
                "sigma_3": [-100.0, -100.0],
                "sigma1_sigma3_diff": [0.0, 150.0],
            },
        )

        current_test_type = CRS
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "yy_strain": [0.0, -0.1],
                "sigma_xx": [-80.0, -120.0],
                "sigma_yy": [-100.0, -180.0],
                "time_steps": [0.0, 12.0],
            },
        )

        current_test_type = DIRECT_SHEAR
        self.assertDictEqual(result_manager.get_experimental_results(), {})

    def test_import_csv_lab_results_keeps_manual_mapping_for_multiple_test_types(self):
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

        current_test_type = TRIAXIAL
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "yy_strain": [0.0, -0.1],
                "sigma1_sigma3_diff": [0.0, 150.0],
            },
        )

        current_test_type = CRS
        self.assertDictEqual(
            result_manager.get_experimental_results(),
            {
                "yy_strain": [0.0, -0.1],
                "sigma_xx": [-80.0, -120.0],
                "sigma_yy": [-100.0, -180.0],
                "time_steps": [0.0, 10.0],
            },
        )

        current_test_type = DIRECT_SHEAR
        self.assertDictEqual(result_manager.get_experimental_results(), {})

    def test_import_csv_lab_results_infers_crs_target_from_sigma_xx_sigma_yy(self):
        current_test_type = TRIAXIAL
        current_test_getter = lambda: current_test_type
        result_manager = ResultManager(current_test_getter)

        with TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / "crs_mapping.csv"
            csv_content = (
                "sigma;epsilon\n"
                "100.0;200.0\n"
                "110.0;220.0\n"
            )
            csv_file.write_text(csv_content, encoding="utf-8")

            imported_test_type = result_manager.import_csv_lab_results(
                csv_file,
                column_mapping={
                    "sigma_xx": "sigma",
                    "sigma_yy": "epsilon",
                },
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


if __name__ == "__main__":
    unittest.main()
