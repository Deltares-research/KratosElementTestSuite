from typing import Callable, Dict, List, Optional
from pathlib import Path
import importlib.util

from kratos_element_test.model.io.lab_results_csv_parser import (
    parse_csv_lab_results,
    get_csv_headers,
    get_expected_columns_for_test_type,
    suggest_csv_column_mapping,
)
from kratos_element_test.view.ui_constants import TYPE_TO_TEST_NAME, TEST_NAME_TO_TYPE


class ResultManager:
    """
    This class manages all results that can be displayed or exported in the GUI.
    """

    def __init__(self, active_test_getter: Callable[[], str]):
        """
        :param active_test_getter: callable which returns the currently active test
        """
        self._simulation_results: Dict[str, Dict[str, List[float]]] = {}
        self._experimental_results: Dict[str, Dict[str, List[float]]] = {}
        self._active_test_getter = active_test_getter

    def get_results_of_active_test_type(self) -> Optional[Dict[str, List[float]]]:
        return self._simulation_results.get(self.get_current_test())

    def set_results_of_active_test_type(self, results: Dict[str, List[float]]):
        self._simulation_results[self._active_test_getter()] = results

    def get_current_test(self) -> str:
        return self._active_test_getter()

    def clear_results(self) -> None:
        self._simulation_results.clear()

    def get_experimental_results(self) -> Dict[str, List[float]]:
        return self._experimental_results.get(self.get_current_test(), {})

    def set_experimental_results_for_test_type(
        self, test_type: str, results: Dict[str, List[float]]
    ) -> None:
        self._experimental_results[test_type] = results

    def clear_experimental_results(self) -> None:
        self._experimental_results.clear()

    def import_lab_results_dict(
        self,
        experimental_by_test: Dict[str, Dict[str, List[float]]],
        clear_existing: bool = True,
    ) -> None:
        if not isinstance(experimental_by_test, dict) or not experimental_by_test:
            raise ValueError(
                "No non-empty 'experimental_by_test' dict found in lab results input"
            )

        if clear_existing:
            self.clear_experimental_results()

        for test_type, results in experimental_by_test.items():
            if not isinstance(test_type, str):
                continue
            if not isinstance(results, dict) or not results:
                continue

            storage_key = TYPE_TO_TEST_NAME.get(test_type, test_type)
            self.set_experimental_results_for_test_type(storage_key, results)

    def import_python_lab_results(self, py_file: Path) -> None:
        module_spec = importlib.util.spec_from_file_location(
            "lab_results_module", str(py_file)
        )
        if module_spec is None or module_spec.loader is None:
            raise ValueError(f"Cannot load lab results file: {py_file}")

        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)

        experimental_by_test = getattr(module, "experimental_by_test", None)
        if not isinstance(experimental_by_test, dict):
            raise ValueError(
                "No non-empty 'experimental_by_test' dict found in lab results input"
            )
        self.import_lab_results_dict(experimental_by_test)

    def prepare_csv_import(self, file_path, test_display_name):
        selected_file = Path(file_path)

        if selected_file.suffix.lower() != ".csv":
            return None

        file_headers = get_csv_headers(selected_file)

        internal_name = TEST_NAME_TO_TYPE.get(test_display_name)
        if not internal_name:
            raise ValueError(f"Unknown test type '{test_display_name}'")

        expected_headers = get_expected_columns_for_test_type(internal_name)

        suggested_mapping = suggest_csv_column_mapping(
            file_headers, expected_headers
        )

        return {
            "file_path": selected_file,
            "file_headers": file_headers,
            "expected_headers": expected_headers,
            "suggested_mapping": suggested_mapping,
            "internal_test_name": internal_name,
        }

    def import_csv_lab_results(
        self,
        csv_file: Path,
        column_mapping: Optional[Dict[str, str]] = None,
        target_test_type: Optional[str] = None,
    ) -> str:
        current_test = self.get_current_test()
        if not current_test or current_test.strip() == "":
            raise ValueError(
                "No active test selected. Please select a test (Triaxial, Direct Simple Shear, or CRS) "
                "before importing CSV data."
            )

        selected_test = target_test_type or current_test
        effective_target_test_type = TEST_NAME_TO_TYPE.get(selected_test, selected_test)

        experimental_by_test = parse_csv_lab_results(
            csv_file,
            default_test_type=effective_target_test_type,
            column_mapping=column_mapping,
        )

        selected_test_results = experimental_by_test.get(effective_target_test_type, {})
        if not selected_test_results:
            selected_display_name = TYPE_TO_TEST_NAME.get(
                effective_target_test_type, effective_target_test_type
            )
            raise ValueError(
                f"CSV does not contain data for the selected test '{selected_display_name}'."
            )

        # Keep previously imported data for other tests; only replace imported tests.
        self.import_lab_results_dict(
            {effective_target_test_type: selected_test_results},
            clear_existing=False,
        )
        return effective_target_test_type
