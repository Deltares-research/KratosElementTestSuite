# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl
from pathlib import Path
from typing import Callable
import importlib.util

from kratos_element_test.controller.material_input_controller import (
    MaterialInputController,
)
from kratos_element_test.controller.result_controller import ResultController
from kratos_element_test.controller.soil_test_input_controller import (
    SoilTestInputController,
)
from kratos_element_test.model.main_model import MainModel
from kratos_element_test.view.result_exporter import (
    export_excel_by_test_type,
)
from kratos_element_test.view.ui_constants import (
    TEST_NAME_TO_TYPE,
)


class ElementTestController:
    def __init__(
        self,
        logger: Callable[[str, str], None],
    ):
        self._logger = logger
        self._main_model = MainModel(logger)

        self._soil_test_input_controller = SoilTestInputController(
            self._main_model.get_soil_test_input_manager()
        )
        self._result_controller = ResultController(
            self._main_model.get_result_manager()
        )
        self._material_input_controller = MaterialInputController(
            self._main_model.get_material_input_manager()
        )

    def run(self) -> bool:
        try:
            self._main_model.run_simulation()
        except Exception as e:
            self._logger(f"Simulation failed: {e}", "error")
            return False
        return True

    def get_current_test_type(self) -> str:
        return self._main_model.get_current_test_type()

    def export_latest_results(self):
        results = self._result_controller.get_latest_results()
        test_type = TEST_NAME_TO_TYPE.get(self._result_controller.get_current_test())
        if not results:
            raise ValueError("No results available for export")
        export_excel_by_test_type(results, test_type)

    def _import_lab_results(self, py_file: Path) -> None:
        spec = importlib.util.spec_from_file_location("lab_results_module", str(py_file))
        if spec is None or spec.loader is None:
            raise ValueError(f"Cannot load lab results file: {py_file}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        experimental = getattr(module, "experimental", None)
        if not isinstance(experimental, dict) or not experimental:
            raise ValueError("No 'experimental' dict found in lab results file")

        # Store for current active test
        self._result_controller.set_experimental_results(experimental)

    def set_material_type(self, material_type: str) -> None:
        self._main_model.set_material_type(material_type)

    def parse_udsm(self, dll_path: Path):
        self._main_model.initialize_udsm(dll_path)
