# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

from typing import Optional, Callable, List, Tuple, Dict

from kratos_element_test.controller.soil_test_input_controller import (
    SoilTestInputController,
)
from kratos_element_test.model.main_model import MainModel
from kratos_element_test.model.models import MohrCoulombOptions
from kratos_element_test.model.pipeline.run_simulation import RunSimulation
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
        self.latest_results = None
        self.latest_test_type = None
        self._logger = logger
        self._plotter_factory = plotter_factory

        self._mc_enabled: bool = False
        self._mc_indices: Tuple[Optional[int], Optional[int]] = (None, None)

        self._drainage: str = "drained"
        self._main_model = MainModel(logger)

        self._soil_test_input_controller = SoilTestInputController(
            self._main_model.soil_test_input_manager
        )

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

    def set_drainage(self, drainage: str, test_type: str) -> None:
        if not self._is_valid_drainage(drainage):
            return

        # For now we save the drainage in two places, in the next PR we will
        # refactor to have a single source of truth (i.e. the SoilTestInputManager)
        self._main_model.soil_test_input_manager.update_drainage(drainage, test_type)
        self._drainage = drainage

    def run(
        self,
        *,
        axes,
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

            self._main_model.run_simulation(self._drainage, dll_path, udsm_number, mohr_coulomb_options, material_parameters)
            self.latest_results = self._main_model.get_latest_results()

            plotter = self._plotter_factory(axes)
            self._render(self.latest_results, plotter, test_type)
            self.latest_test_type = test_type

        except Exception as e:
            self._logger(f"Simulation failed: {e}", "error")
            return False
        return True

    def _render(self, results: Dict[str, List[float]], plotter, test_type) -> None:
        if not plotter:
            self._logger(
                "No plotter was provided; using a no-op plotter (headless run).", "info"
            )
            return

        if test_type == "triaxial":
            plotter.triaxial(
                results["yy_strain"],
                results["vol_strain"],
                results["sigma1"],
                results["sigma3"],
                results["mean_stress"],
                results["von_mises"],
                results["cohesion"],
                results["phi"],
            )
        elif test_type == "direct_shear":
            plotter.direct_shear(
                results["shear_strain_xy"],
                results["shear_xy"],
                results["sigma1"],
                results["sigma3"],
                results["mean_stress"],
                results["von_mises"],
                results["cohesion"],
                results["phi"],
            )
        elif test_type == "crs":
            plotter.crs(
                results["yy_strain"],
                results["time_steps"],
                results["sigma_yy"],
                results["sigma_xx"],
                results["mean_stress"],
                results["von_mises"],
                results["sigma1"],
                results["sigma3"],
                results["cohesion"],
                results["phi"],
            )
        else:
            raise ValueError(f"Unsupported test_type: {test_type}")

    def get_current_test_type(self) -> str:
        return self._main_model.get_current_test_type()