from typing import Callable, Dict, List, Optional
from pathlib import Path
import importlib.util

from kratos_element_test.model.io.lab_results_csv_parser import (
    infer_test_type_from_columns,
    parse_csv_lab_results,
)
from kratos_element_test.view.ui_constants import TYPE_TO_TEST_NAME


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
        self, experimental_by_test: Dict[str, Dict[str, List[float]]]
    ) -> None:
        if not isinstance(experimental_by_test, dict) or not experimental_by_test:
            raise ValueError(
                "No non-empty 'experimental_by_test' dict found in lab results input"
            )

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
        self.import_lab_results_dict(experimental_by_test)

    def import_csv_lab_results(
        self,
        csv_file: Path,
        column_mapping: Optional[Dict[str, str]] = None,
        target_test_type: Optional[str] = None,
    ) -> str:
        effective_target_test_type = target_test_type
        if effective_target_test_type is None:
            effective_target_test_type = infer_test_type_from_columns(
                list((column_mapping or {}).keys()),
                fallback_test_type=self.get_current_test(),
            )

        experimental_by_test = parse_csv_lab_results(
            csv_file,
            default_test_type=effective_target_test_type or self.get_current_test(),
            column_mapping=column_mapping,
        )
        self.import_lab_results_dict(experimental_by_test)
        return effective_target_test_type or self.get_current_test()
