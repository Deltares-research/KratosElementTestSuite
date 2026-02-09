from kratos_element_test.model.material_input_data_models import (
    LinearElasticMaterialInputs,
    MohrCoulombMaterialInputs,
    UDSMMaterialInputs,
)
from kratos_element_test.model.material_input_manager import MaterialInputManager
from kratos_element_test.view.ui_constants import UI_NAME_TO_KRATOS_NAME


class MaterialInputController:
    def __init__(self, material_input_manager: MaterialInputManager):
        self._material_input_manager = material_input_manager

    def get_current_material_inputs(
        self,
    ) -> LinearElasticMaterialInputs | MohrCoulombMaterialInputs | UDSMMaterialInputs:
        return self._material_input_manager.get_current_material_inputs()

    def bind_material_input_fields_to_update_functions(self, string_vars) -> None:
        for key, string_var in string_vars.items():
            string_var.trace_add(
                "write",
                lambda _var_name, _index, _operation, captured_changed_variable=key, captured_string_var=string_var: self._material_input_manager.update_material_parameter_of_current_type(
                    key=UI_NAME_TO_KRATOS_NAME.get(
                        captured_changed_variable, captured_changed_variable
                    ),
                    value=float(captured_string_var.get()),
                ),
            )

    def set_current_udsm_model(self, model_name):
        self._material_input_manager.set_current_udsm_model(model_name)

    def get_udsm_model_names(self):
        return self._material_input_manager.get_udsm_model_names()

    def get_current_material_type(self):
        return self._material_input_manager.get_current_material_type()

    def set_mohr_enabled(self, enabled):
        self._material_input_manager.set_mohr_enabled(enabled)

    def get_mohr_enabled(self):
        return self._material_input_manager.get_mohr_enabled()

    def set_cohesion_index(self, cohesion_index):
        self._material_input_manager.set_cohesion_index(cohesion_index)

    def set_phi_index(self, phi_index):
        self._material_input_manager.set_phi_index(phi_index)
