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

    def add_crs_strain_increment(self) -> None:
        self._soil_test_input_manager.add_strain_increment()

    def remove_last_crs_strain_increment(self):
        self._soil_test_input_manager.remove_last_crs_strain_increment()

    def bind_test_input_fields_to_update_functions(
        self, widgets, test_type: str
    ) -> None:
        widgets[INIT_PRESSURE_LABEL].bind(
            "<FocusOut>",
            lambda e: self._soil_test_input_manager.update_init_pressure(
                new_pressure=float(widgets[INIT_PRESSURE_LABEL].get()),
                test_type=test_type,
            ),
        )
        widgets[MAX_STRAIN_LABEL].bind(
            "<FocusOut>",
            lambda e: self._soil_test_input_manager.update_max_strain(
                new_strain=float(widgets[MAX_STRAIN_LABEL].get()), test_type=test_type
            ),
        )
        widgets[NUM_STEPS_LABEL].bind(
            "<FocusOut>",
            lambda e: self._soil_test_input_manager.update_num_steps(
                new_steps=int(widgets[NUM_STEPS_LABEL].get()), test_type=test_type
            ),
        )
        widgets[DURATION_LABEL].bind(
            "<FocusOut>",
            lambda e: self._soil_test_input_manager.update_duration(
                new_duration=float(widgets[DURATION_LABEL].get()), test_type=test_type
            ),
        )

    def bind_crs_test_input_row_to_update_functions(
        self, row, current_index: int
    ) -> None:
        row[DURATION_LABEL].bind(
            "<FocusOut>",
            lambda e, idx=current_index: self._soil_test_input_manager.set_crs_duration(
                new_duration_in_hours=float(row[DURATION_LABEL].get()), index=idx
            ),
        )
        row[STRAIN_INCREMENT_LABEL].bind(
            "<FocusOut>",
            lambda e, idx=current_index: self._soil_test_input_manager.set_crs_strain_increment(
                new_increment=float(row[STRAIN_INCREMENT_LABEL].get()), index=idx
            ),
        )
        row[STEPS_LABEL].bind(
            "<FocusOut>",
            lambda e, idx=current_index: self._soil_test_input_manager.set_crs_steps(
                new_steps=int(row[STEPS_LABEL].get()), index=idx
            ),
        )
