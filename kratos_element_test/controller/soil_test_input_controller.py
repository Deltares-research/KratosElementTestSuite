from typing import Callable, Optional
from kratos_element_test.model.models import (
    TriaxialAndShearSimulationInputs,
    CRSSimulationInputs,
)
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

    def get_current_test_inputs(
        self,
    ) -> TriaxialAndShearSimulationInputs | CRSSimulationInputs:
        return self._soil_test_input_manager.get_current_test_inputs()

    def add_crs_strain_increment(self) -> None:
        self._soil_test_input_manager.add_strain_increment()

    def remove_last_crs_strain_increment(self):
        self._soil_test_input_manager.remove_last_crs_strain_increment()

    def bind_test_input_fields_to_update_functions(
        self, string_vars, test_type: str
    ) -> None:
        string_vars[INIT_PRESSURE_LABEL].trace_add(
            "write",
            lambda _var_name, _index, _operation: self._soil_test_input_manager.update_init_pressure(
                new_pressure=float(string_vars[INIT_PRESSURE_LABEL].get()),
                test_type=test_type,
            ),
        )
        string_vars[MAX_STRAIN_LABEL].trace_add(
            "write",
            lambda _var_name, _index, _operation: self._soil_test_input_manager.update_max_strain(
                new_strain=float(string_vars[MAX_STRAIN_LABEL].get()),
                test_type=test_type,
            ),
        )
        string_vars[NUM_STEPS_LABEL].trace_add(
            "write",
            lambda _var_name, _index, _operation: self._soil_test_input_manager.update_num_steps(
                new_steps=int(string_vars[NUM_STEPS_LABEL].get()), test_type=test_type
            ),
        )
        string_vars[DURATION_LABEL].trace_add(
            "write",
            lambda _var_name, _index, _operation: self._soil_test_input_manager.update_duration(
                new_duration_in_seconds=float(string_vars[DURATION_LABEL].get()),
                test_type=test_type,
            ),
        )

    def bind_crs_test_input_row_to_update_functions(
        self, string_vars, current_index: int
    ) -> None:
        string_vars[DURATION_LABEL].trace_add(
            "write",
            lambda _var_name, _index, _operation: self._soil_test_input_manager.set_crs_duration(
                new_duration_in_hours=float(string_vars[DURATION_LABEL].get()),
                index=current_index,
            ),
        )
        string_vars[STRAIN_INCREMENT_LABEL].trace_add(
            "write",
            lambda _var_name, _index, _operation: self._soil_test_input_manager.set_crs_strain_increment(
                new_increment=float(string_vars[STRAIN_INCREMENT_LABEL].get()),
                index=current_index,
            ),
        )
        string_vars[STEPS_LABEL].trace_add(
            "write",
            lambda _var_name, _index, _operation: self._soil_test_input_manager.set_crs_steps(
                new_steps=int(string_vars[STEPS_LABEL].get()), index=current_index
            ),
        )

    def bind_drainage_combo_box(
        self, combo_box, on_drainage_changed: Optional[Callable[[int], None]] = None
    ):
        def _sync_drainage_from_combobox(event=None) -> None:
            val = combo_box.get().strip().lower()
            self._soil_test_input_manager.update_drainage(val)

            if (
                on_drainage_changed is not None
                and self.get_current_test_type() == DIRECT_SHEAR
            ):
                num_plots = 5 if val == "undrained" else 4
                on_drainage_changed(num_plots=num_plots)

        combo_box.bind("<<ComboboxSelected>>", _sync_drainage_from_combobox)

    def set_current_test_type(self, test_type: str) -> None:
        self._soil_test_input_manager.set_current_test_type(test_type)

    def get_current_test_type(self) -> str:
        return self._soil_test_input_manager.get_current_test_type()
