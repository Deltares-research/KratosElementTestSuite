# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

from typing import Optional, Callable, List, Tuple
from kratos_element_test.core.pipeline.run_simulation import RunSimulation
from kratos_element_test.core.models import SimulationInputs, MohrCoulombOptions
from kratos_element_test.ui.ui_constants import VALID_TEST_TYPES, VALID_DRAINAGE_TYPES


class ElementTestController:
    def __init__(self, logger: Callable[[str, str], None], plotter_factory: Callable[[object], object]):
        self._logger = logger
        self._plotter_factory = plotter_factory

        # Mohr–Coulomb state
        self._mc_enabled: bool = False
        self._mc_indices: Tuple[Optional[int], Optional[int]] = (None, None)  # (c_idx, phi_idx)

        self._test_type: Optional[str] = None
        self._drainage: str = "drained"

    def set_mohr_enabled(self, enabled: bool) -> None:
        self._mc_enabled = bool(enabled)
        self._logger(f"Mohr-Coulomb model {'enabled' if enabled else 'disabled'}.", "info")

    def set_mohr_mapping(self, c_index: Optional[int], phi_index: Optional[int]) -> None:
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

    def set_test_type(self, test_type: str) -> None:
        if not self._is_valid_test_type(test_type):
            return
        self._test_type = test_type

    def _is_valid_drainage(self, drainage: Optional[str]) -> bool:
        if drainage in VALID_DRAINAGE_TYPES:
            return True
        self._logger(f"Unknown drainage: {drainage}", "warn")
        return False

    def set_drainage(self, drainage: str) -> None:
        if not self._is_valid_drainage(drainage):
            return
        self._drainage = drainage

    def run(self,
            *,
            axes,
            test_type: Optional[str] = None,
            dll_path: str,
            index: Optional[int],
            material_parameters: List[float],
            sigma_init: float,
            eps_max: float,
            n_steps: float,
            duration: float,
            # stage_durations: Optional[List[float]] = None,
            # strain_incs: Optional[List[float]] = None,
            # step_counts: Optional[List[int]] = None
            ) -> None:

        tt = test_type or self._test_type
        if not self._is_valid_test_type(tt):
            self._logger("Please select a test type.", "error")
            return

        inputs = SimulationInputs(
            test_type=tt,
            maximum_strain=eps_max,
            initial_effective_cell_pressure=sigma_init,
            stress_increment=0.0,
            number_of_steps=int(n_steps),
            duration=duration,
            drainage=self._drainage,
            mohr_coulomb=MohrCoulombOptions(
                enabled=self._mc_enabled,
                c_index=self._mc_indices[0],
                phi_index=self._mc_indices[1],
            ),
        )

        try:
            inputs.validate()
        except ValueError as e:
            self._logger(str(e), "error")
            return

        plotter = self._plotter_factory(axes)

        try:
            self._logger(f"MC indices: {self._mc_tuple()}", "info")

            RunSimulation.run_simulation(
                test_type=inputs.test_type,
                drainage=inputs.drainage,
                dll_path=dll_path or "",
                index=index,
                material_parameters=material_parameters,
                num_steps=inputs.number_of_steps if not hasattr(self, "step_counts") or self.step_counts is None else self.step_counts,
                end_time=inputs.duration,
                maximum_strain=inputs.maximum_strain,
                initial_effective_cell_pressure=inputs.initial_effective_cell_pressure,
                cohesion_phi_indices=inputs.mohr_coulomb.to_indices(),
                plotter=plotter,
                logger=self._logger,
                stage_durations=getattr(self, "stage_durations", None),
                step_counts=getattr(self, "step_counts", None),
                strain_incs=getattr(self, "strain_incs", None)
            )

        except Exception as e:
            self._logger(f"Simulation failed: {e}", "error")
            raise
