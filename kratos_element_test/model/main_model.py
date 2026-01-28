from typing import Callable, Dict, List

from kratos_element_test.model.material_input_manager import MaterialInputManager
from kratos_element_test.model.material_inputs import MohrCoulombOptions
from kratos_element_test.model.pipeline.run_simulation import RunSimulation
from kratos_element_test.model.result_manager import ResultManager
from kratos_element_test.model.soil_test_input_manager import SoilTestInputManager


class MainModel:
    def __init__(self, logger: Callable[[str, str], None]):
        self._logger = logger
        self._material_input_manager = MaterialInputManager()
        self._soil_test_input_manager = SoilTestInputManager()
        self._result_manager = ResultManager(
            self._soil_test_input_manager.get_current_test_type
        )

    def get_current_test_type(self) -> str:
        return self._soil_test_input_manager.get_current_test_type()

    def run_simulation(
        self,
        model_name: str,
        udsm_number: int,
        mohr_coulomb_options: MohrCoulombOptions,
        material_parameters,
    ) -> None:

        inputs = self._soil_test_input_manager.get_current_test_inputs()
        try:
            inputs.validate()
        except ValueError:
            self._logger("Calculation stopped due to invalid input.", "error")
            raise

        sim = RunSimulation(
            test_inputs=inputs,
            material_inputs=self._material_input_manager.get_current_material_inputs(),
            model_name=model_name,
            udsm_number=udsm_number,
            material_parameters=material_parameters,
            cohesion_phi_indices=mohr_coulomb_options.to_indices(),
            logger=self._logger,
        )

        sim.run()
        self._result_manager.set_results_of_active_test_type(
            sim.post_process_results(),
        )

    def get_latest_results(self) -> Dict[str, List[float]]:
        return self._result_manager.get_results_of_active_test_type()

    def get_result_manager(self) -> ResultManager:
        return self._result_manager

    def get_soil_test_input_manager(self):
        return self._soil_test_input_manager

    def clear_results(self) -> None:
        self._result_manager.clear_results()

    def set_material_type(self, material_type: str):
        self._material_input_manager.set_current_material_type(material_type)
        self.clear_results()

    def get_material_input_manager(self) -> MaterialInputManager:
        return self._material_input_manager

    def initialize_udsm(self, dll_path):
        self._material_input_manager.initialize_udsm(dll_path)
