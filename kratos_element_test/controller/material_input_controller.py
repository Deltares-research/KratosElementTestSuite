from kratos_element_test.model.material_input_manager import MaterialInputManager
from kratos_element_test.model.material_inputs import LinearElasticMaterialInputs


class MaterialInputController:
    def __init__(self, material_input_manager: MaterialInputManager):
        self._material_input_manager = material_input_manager

    def get_current_material_inputs(self) -> LinearElasticMaterialInputs:
        return self._material_input_manager.get_current_material_inputs()

    def bind_test_input_fields_to_update_functions(self, string_vars) -> None:
        for key, string_var in string_vars.items():
            string_var.trace_add(
                "write",
                lambda _var_name, _index, _operation, changed_variable=key, string_var_test=string_var: self._material_input_manager.update_material_parameter_of_current_type(
                    key=changed_variable, value=float(string_var_test.get())
                ),
            )

    def set_current_udsm_model(self, model_name):
        self._material_input_manager.set_current_udsm_model(model_name)

    def get_udsm_model_names(self):
        return self._material_input_manager.get_udsm_model_names()

    def get_current_material_type(self):
        return self._material_input_manager.get_current_material_type()

    def set_mohr_mapping(self, c_index, phi_index):
        self._material_input_manager.set_mohr_mapping(c_index, phi_index)

    def set_mohr_enabled(self, enabled):
        self._material_input_manager.set_mohr_enabled(enabled)
