from kratos_element_test.model.models import TriaxialAndShearSimulationInputs
from kratos_element_test.model.soil_test_input_manager import SoilTestInputManager
from kratos_element_test.view.ui_constants import (
    TRIAXIAL,
    DIRECT_SHEAR,
    CRS,
    INIT_PRESSURE_LABEL,
    MAX_STRAIN_LABEL,
    NUM_STEPS_LABEL,
    DURATION_LABEL,
    STRAIN_INCREMENT_LABEL,
    STEPS_LABEL,
)


class SoilTestInputController:
    def __init__(self, soil_test_input_manager: SoilTestInputManager):
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
        self._soil_test_input_manager.remove_last_crs_strain_increment()

    def bind_test_input_fields_to_update_functions(
        self, widgets, test_type: str
    ) -> None:
        widgets[INIT_PRESSURE_LABEL].bind(
            "<FocusOut>",
            lambda e: self.update_init_pressure(
                new_pressure=float(widgets[INIT_PRESSURE_LABEL].get()),
                test_type=test_type,
            ),
        )
        widgets[MAX_STRAIN_LABEL].bind(
            "<FocusOut>",
            lambda e: self.update_max_strain(
                new_strain=float(widgets[MAX_STRAIN_LABEL].get()), test_type=test_type
            ),
        )
        widgets[NUM_STEPS_LABEL].bind(
            "<FocusOut>",
            lambda e: self.update_num_steps(
                new_steps=int(widgets[NUM_STEPS_LABEL].get()), test_type=test_type
            ),
        )
        widgets[DURATION_LABEL].bind(
            "<FocusOut>",
            lambda e: self.update_duration(
                new_duration=float(widgets[DURATION_LABEL].get()), test_type=test_type
            ),
        )

    def bind_crs_test_input_row_to_update_functions(
        self, row, current_index: int
    ) -> None:
        row[DURATION_LABEL].bind(
            "<FocusOut>",
            lambda e, idx=current_index: self.update_crs_duration(
                new_duration=float(row[DURATION_LABEL].get()), index=idx
            ),
        )
        row[STRAIN_INCREMENT_LABEL].bind(
            "<FocusOut>",
            lambda e, idx=current_index: self.update_crs_strain_increment(
                new_strain_increment=float(row[STRAIN_INCREMENT_LABEL].get()), index=idx
            ),
        )
        row[STEPS_LABEL].bind(
            "<FocusOut>",
            lambda e, idx=current_index: self.update_crs_number_of_steps(
                new_steps=int(row[STEPS_LABEL].get()), index=idx
            ),
        )
