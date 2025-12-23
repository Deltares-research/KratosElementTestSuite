from kratos_element_test.model.models import TriaxialAndShearSimulationInputs
from kratos_element_test.view.ui_constants import (
    TRIAXIAL,
    DIRECT_SHEAR,
    CRS,
    INIT_PRESSURE_LABEL,
    MAX_STRAIN_LABEL,
    NUM_STEPS_LABEL,
    DURATION_LABEL,
)


class SoilTestInputController:
    def __init__(self, soil_test_input_manager):
        self._soil_test_input_manager = soil_test_input_manager

    def get_triaxial_inputs(self) -> TriaxialAndShearSimulationInputs:
        return self._soil_test_input_manager.input_data.get(TRIAXIAL)

    def get_shear_inputs(self) -> TriaxialAndShearSimulationInputs:
        return self._soil_test_input_manager.input_data.get(DIRECT_SHEAR)

    def get_crs_inputs(self):
        return self._soil_test_input_manager.input_data.get(CRS)

    def update_crs_duration(self, new_duration: float, index: int) -> None:
        self._soil_test_input_manager.set_crs_duration(index, new_duration)

    def update_crs_strain_increment(
        self, new_strain_increment: float, index: int
    ) -> None:
        self._soil_test_input_manager.set_crs_strain_increment(
            index, new_strain_increment
        )

    def update_crs_number_of_steps(self, new_steps: int, index: int) -> None:
        self._soil_test_input_manager.set_crs_steps(index, new_steps)

    def update_init_pressure(self, new_pressure: float, test_type: str) -> None:
        self._soil_test_input_manager.input_data[
            test_type
        ].initial_effective_cell_pressure = new_pressure

    def update_max_strain(self, new_strain: float, test_type: str) -> None:
        self._soil_test_input_manager.input_data[test_type].maximum_strain = new_strain

    def update_num_steps(self, new_steps: int, test_type: str) -> None:
        self._soil_test_input_manager.input_data[test_type].number_of_steps = new_steps

    def update_duration(self, new_duration: float, test_type: str) -> None:
        self._soil_test_input_manager.input_data[test_type].duration_in_hours = (
            new_duration
        )

    def add_crs_strain_increment(self) -> None:
        self._soil_test_input_manager.add_strain_increment()

    def remove_last_crs_strain_increment(self):
        pass
        if len(self._soil_test_input_manager.input_data[CRS].strain_increments) > 1:
            self._soil_test_input_manager.input_data[CRS].strain_increments.pop()
        else:
            self._logger(
                "Cannot remove the last CRS strain increment; at least one must remain.",
                "warn",
            )

    def bind_widgets_to_handling_functions(self, widgets, test_type: str) -> None:
        widgets[INIT_PRESSURE_LABEL].bind("<FocusOut>", lambda e: self.update_init_pressure(
            new_pressure=float(widgets[INIT_PRESSURE_LABEL].get()), test_type=test_type
        ))
        widgets[MAX_STRAIN_LABEL].bind("<FocusOut>", lambda e: self.update_max_strain(
            new_strain=float(widgets[MAX_STRAIN_LABEL].get()), test_type=test_type
        ))
        widgets[NUM_STEPS_LABEL].bind("<FocusOut>", lambda e: self.update_num_steps(
            new_steps=int(widgets[NUM_STEPS_LABEL].get()), test_type=test_type
        ))
        widgets[DURATION_LABEL].bind("<FocusOut>", lambda e: self.update_duration(
            new_duration=float(widgets[DURATION_LABEL].get()), test_type=test_type
        ))
