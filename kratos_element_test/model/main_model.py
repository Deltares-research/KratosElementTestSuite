from typing import Callable

from kratos_element_test.model.models import MohrCoulombOptions
from kratos_element_test.model.pipeline.run_simulation import RunSimulation
from kratos_element_test.model.result_manager import ResultManager
from kratos_element_test.model.soil_test_input_manager import SoilTestInputManager


class MainModel:
    def __init__(self, logger: Callable[[str, str], None]):
        self._logger = logger
        self.soil_test_input_manager = SoilTestInputManager()
        self._latest_results = None
        self._result_manager = ResultManager(
            self.soil_test_input_manager.get_current_test_type
        )

    def get_current_test_type(self) -> str:
        return self.soil_test_input_manager.get_current_test_type()

    def run_simulation(
        self,
        model_name: str,
        dll_path: str | None,
        udsm_number: int,
        mohr_coulomb_options: MohrCoulombOptions,
        material_parameters,
    ) -> None:

        inputs = self.soil_test_input_manager.get_current_test_inputs()
        try:
            inputs.validate()
        except ValueError as e:
            self._logger("Calculation stopped due to invalid input.", "error")
            self._logger(str(e), "error")
            raise e

        sim = RunSimulation(
            test_inputs=inputs,
            model_name=model_name,
            dll_path=dll_path or "",
            udsm_number=udsm_number,
            material_parameters=material_parameters,
            cohesion_phi_indices=mohr_coulomb_options.to_indices(),
            logger=self._logger,
        )

        sim.run()
        self._result_manager.set_results_of_active_test_type(
            sim.post_process_results(),
        )

    def get_latest_results(self):
        return self._result_manager.get_results_of_active_test_type()
