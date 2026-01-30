from tkinter import ttk
import tkinter as tk

from kratos_element_test.view.widget_creation_utils import create_entries


class MaterialInputView(ttk.Frame):
    def __init__(self, material_input_controller, master, **kwargs):
        super().__init__(master, **kwargs)
        self._controller = material_input_controller

        self.is_linear_elastic = (
            self._controller.get_current_material_type() == "linear_elastic"
        )
        self.is_mohr_coulomb = (
            self._controller.get_current_material_type() == "mohr_coulomb"
        )

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()

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
        self.setup_mohr_coulomb_controls(params)

    def _create_mohr_options(self, params):
        self.mohr_frame = ttk.Frame(self)
        self.mohr_frame.pack(fill="x", padx=10, pady=5)
        self.mohr_checkbox_widget = ttk.Checkbutton(
            self.mohr_frame,
            text="Mohr-Coulomb Model",
            variable=self.mohr_checkbox,
            command=self._toggle_mohr_options,
        )
        self.mohr_checkbox_widget.pack(side="left")

        self.c_label = ttk.Label(self.mohr_frame, text="Indices (1-based): Cohesion")
        self.c_dropdown = ttk.Combobox(
            self.mohr_frame,
            textvariable=self.cohesion_var,
            values=[str(i + 1) for i in range(len(params))],
            state="readonly",
            width=2,
        )

        self.phi_label = ttk.Label(self.mohr_frame, text="Friction Angle")
        self.phi_dropdown = ttk.Combobox(
            self.mohr_frame,
            textvariable=self.phi_var,
            values=[str(i + 1) for i in range(len(params))],
            state="readonly",
            width=2,
        )

        def _sync_mapping(*_):
            c_idx, phi_idx = self._parse_mc_indices()
            self._controller.set_mohr_mapping(c_idx, phi_idx)

        self.c_dropdown.bind("<<ComboboxSelected>>", _sync_mapping)
        self.phi_dropdown.bind("<<ComboboxSelected>>", _sync_mapping)

        _sync_mapping()

    def _parse_mc_indices(self):
        try:
            c_idx = int(self.cohesion_var.get()) if self.cohesion_var.get() else None
            phi_idx = int(self.phi_var.get()) if self.phi_var.get() else None
        except ValueError:
            c_idx, phi_idx = None, None

        return c_idx, phi_idx

    def _toggle_mohr_options(self):
        widgets = [self.c_label, self.c_dropdown, self.phi_label, self.phi_dropdown]
        if self.mohr_checkbox.get():

            self._controller.set_mohr_enabled(True)
            c_idx, phi_idx = self._parse_mc_indices()
            self._controller.set_mohr_mapping(c_idx, phi_idx)

            for w in widgets:
                w.pack(side="left", padx=5)

        else:
            self._controller.set_mohr_enabled(False)
            self._controller.set_mohr_mapping(None, None)

            for w in widgets:
                w.pack_forget()

    def setup_mohr_coulomb_controls(self, params):
        self.mohr_checkbox = tk.BooleanVar()
        self.cohesion_var = tk.StringVar(value="3")
        self.phi_var = tk.StringVar(value="4")
        self._create_mohr_options(params)

        if self.is_linear_elastic:
            self.mohr_frame.pack_forget()

        elif self.is_mohr_coulomb:
            self.mohr_frame.pack_forget()

        else:
            self.mohr_checkbox_widget.configure(state="normal")
