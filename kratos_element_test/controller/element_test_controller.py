# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl
from pathlib import Path
from typing import Optional, Callable

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

    def set_mohr_enabled(self, enabled: bool) -> None:
        self._material_input_controller.set_mohr_enabled(enabled)
        self._logger(
            f"Mohr-Coulomb model {'enabled' if enabled else 'disabled'}.", "info"
        )

    def set_mohr_mapping(
        self, c_index: Optional[int], phi_index: Optional[int]
    ) -> None:
        self._material_input_controller.set_mohr_mapping(c_index, phi_index)

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

    def clear_results(self) -> None:
        self._main_model.clear_results()

    def set_material_type(self, material_type: str) -> None:
        self._main_model.set_material_type(material_type)

    def parse_udsm(self, dll_path: Path):
        self._main_model.initialize_udsm(dll_path)
