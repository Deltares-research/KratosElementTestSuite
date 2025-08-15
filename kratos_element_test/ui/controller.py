# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

from typing import Optional, Callable, List, Tuple
from kratos_element_test.core.pipeline.run_simulation import run_simulation


class ElementTestController:
    def __init__(self, logger: Callable[[str, str], None], plotter_factory: Callable[[object], object]):
        self._logger = logger
        self._plotter_factory = plotter_factory

        # Mohr–Coulomb state
        self._mc_enabled: bool = False
        self._mc_indices: Tuple[Optional[int], Optional[int]] = (None, None)  # (c_idx, phi_idx)

    def set_mohr_enabled(self, enabled: bool) -> None:
        self._mc_enabled = bool(enabled)
        self._logger(f"Mohr-Coulomb {'enabled' if enabled else 'disabled'}.", "info")

    def set_mohr_mapping(self, c_index: Optional[int], phi_index: Optional[int]) -> None:
        self._mc_indices = (c_index, phi_index)

    def _mc_tuple(self) -> Optional[Tuple[int, int]]:
        if not self._mc_enabled:
            return None
        c_idx, phi_idx = self._mc_indices
        if c_idx is None or phi_idx is None:
            return None
        return c_idx, phi_idx

    def run(self,
            *,
            axes,
            test_type: str,
            dll_path: str,
            index: Optional[int],
            material_parameters: List[float],
            sigma_init: float,
            eps_max: float,
            n_steps: float,
            duration: float) -> None:
        plotter = self._plotter_factory(axes)

        try:
            self._logger(f"MC indices: {self._mc_tuple()}", "info")
            run_simulation(
                test_type=test_type,
                dll_path=dll_path or "",
                index=index,
                material_parameters=material_parameters,
                num_steps=n_steps,
                end_time=duration,
                maximum_strain=eps_max,
                initial_effective_cell_pressure=sigma_init,
                cohesion_phi_indices=self._mc_tuple(),
                plotter=plotter,
                logger=self._logger
            )

        except Exception as e:
            self._logger(f"Simulation failed: {e}", "error")
            raise
