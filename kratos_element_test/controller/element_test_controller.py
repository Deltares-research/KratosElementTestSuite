# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl
from tkinter import messagebox
from typing import Optional, Callable, List, Tuple

from kratos_element_test.controller.result_controller import ResultController
from kratos_element_test.controller.soil_test_input_controller import (
    SoilTestInputController,
)
from kratos_element_test.model.main_model import MainModel
from kratos_element_test.model.models import MohrCoulombOptions
from kratos_element_test.view.result_exporter import (
    export_excel_by_test_type,
)
from kratos_element_test.view.ui_constants import (
    VALID_TEST_TYPES,
    VALID_DRAINAGE_TYPES,
    TEST_NAME_TO_TYPE,
)


class ElementTestController:
    def __init__(
        self,
        logger: Callable[[str, str], None],
        plotter_factory: Callable[[object], object],
    ):
        self._logger = logger
        self._plotter_factory = plotter_factory

        self._mc_enabled: bool = False
        self._mc_indices: Tuple[Optional[int], Optional[int]] = (None, None)

        self._main_model = MainModel(logger)

        self._soil_test_input_controller = SoilTestInputController(
            self._main_model.soil_test_input_manager
        )
        self._result_controller = ResultController(self._main_model._result_manager)

    def set_mohr_enabled(self, enabled: bool) -> None:
        self._mc_enabled = bool(enabled)
        self._logger(
            f"Mohr-Coulomb model {'enabled' if enabled else 'disabled'}.", "info"
        )

    def set_mohr_mapping(
        self, c_index: Optional[int], phi_index: Optional[int]
    ) -> None:
        self._mc_indices = (c_index, phi_index)

    def _mc_tuple(self) -> Optional[Tuple[int, int]]:
        if not self._mc_enabled:
            return None
        c_idx, phi_idx = self._mc_indices
        if c_idx is None or phi_idx is None:
            return None
        return c_idx, phi_idx

    def _is_valid_test_type(self, test_type: Optional[str]) -> bool:
        if test_type in VALID_TEST_TYPES:
            return True
        self._logger(f"Unknown test type: {test_type}", "warn")
        return False

    def _is_valid_drainage(self, drainage: Optional[str]) -> bool:
        if drainage in VALID_DRAINAGE_TYPES:
            return True
        self._logger(f"Unknown drainage: {drainage}", "warn")
        return False

    def run(
        self,
        *,
        model_name: Optional[str] = None,
        dll_path: str,
        udsm_number: Optional[int],
        material_parameters: List[float],
    ) -> bool:
        test_type = TEST_NAME_TO_TYPE.get(
            self._main_model.soil_test_input_manager.get_current_test_type()
        )
        if not self._is_valid_test_type(test_type):
            self._logger("Please select a test type.", "error")
            return False

        try:
            self._logger(f"MC indices: {self._mc_tuple()}", "info")

            mohr_coulomb_options = MohrCoulombOptions(
                enabled=self._mc_enabled,
                c_index=self._mc_indices[0],
                phi_index=self._mc_indices[1],
            )

            self._main_model.run_simulation(
                model_name,
                dll_path,
                udsm_number,
                mohr_coulomb_options,
                material_parameters,
            )

        except Exception as e:
            self._logger(f"Simulation failed: {e}", "error")
            return False
        return True

    def get_current_test_type(self) -> str:
        return self._main_model.get_current_test_type()

    def export_latest_results(self):
        results = self._result_controller.get_latest_results()
        test_type = TEST_NAME_TO_TYPE.get(self._result_controller.get_current_test())
        if not results or not test_type:
            return
        try:
            export_excel_by_test_type(results, test_type)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export Excel file.\n\n{e}")
