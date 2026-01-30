from tkinter import ttk

from kratos_element_test.view.widget_creation_utils import create_entries


class MaterialInputView(ttk.Frame):
    def __init__(self, material_input_controller, master, **kwargs):
        super().__init__(master, **kwargs)
        self._controller = material_input_controller

    def initialize(self):
        params = []
        units = []
        default_values = {}
        inputs = self._controller.get_current_material_inputs()
        for key, parameter in inputs.changeable_material_parameters.items():
            params.append(key)
            units.append(parameter.unit)
            default_values[key] = parameter.value

        self.entry_widgets, self.string_vars = create_entries(
            frame=self,
            title="Soil Input Parameters",
            labels=params,
            units=units,
            defaults=default_values,
        )

        self._controller.bind_test_input_fields_to_update_functions(self.string_vars)
