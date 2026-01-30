from tkinter import ttk
import tkinter as tk

from kratos_element_test.view.ui_constants import INPUT_SECTION_FONT
from kratos_element_test.view.widget_creation_utils import create_entries


class MaterialInputView(ttk.Frame):
    def __init__(self, material_input_controller, master, **kwargs):
        super().__init__(master, **kwargs)
        self.entry_widgets = {}
        self.dropdown_frame = None
        self._controller = material_input_controller
        self.entry_frame = None
        self.is_linear_elastic = (
            self._controller.get_current_material_type() == "linear_elastic"
        )
        self.is_mohr_coulomb = (
            self._controller.get_current_material_type() == "mohr_coulomb"
        )
        self.model_var = tk.StringVar(self)
        self.model_var.set(
            self._controller.get_udsm_model_names()[0]
            if self._controller.get_current_material_type() == "udsm"
            else ""
        )

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()

        self.dropdown_frame = ttk.Frame(self)
        self.dropdown_frame.pack(fill="x")
        self.entry_frame = ttk.Frame(self)
        self.entry_frame.pack(fill="x")
        material_type = self._controller.get_current_material_type()
        if material_type == "udsm" and len(self._controller.get_udsm_model_names()) > 1:
            ttk.Label(
                self.dropdown_frame,
                text="Select a Model:",
                font=(INPUT_SECTION_FONT, 12, "bold"),
            ).pack(anchor="w", padx=5, pady=5)
            self.model_menu = ttk.Combobox(
                self.dropdown_frame,
                textvariable=self.model_var,
                values=self._controller.get_udsm_model_names(),
                state="readonly",
            )
            self.model_menu.pack(side="top", fill="x", expand=True, padx=5)
            self.model_var.trace("w", lambda *args: self.setup_material_inputs())
            self.model_menu.configure(state="readonly")

        self.mohr_frame = ttk.Frame(self)
        self.mohr_frame.pack(fill="x", padx=10, pady=5)

        self.setup_material_inputs()

    def setup_material_inputs(self):
        if self._controller.get_current_material_type() == "udsm":
            self._controller.set_current_udsm_model(self.model_var.get())
        for entry in (
            self.entry_frame.winfo_children() + self.mohr_frame.winfo_children()
        ):
            entry.destroy()

        params = []
        units = []
        default_values = {}
        inputs = self._controller.get_current_material_inputs()
        for key, parameter in inputs.changeable_material_parameters.items():
            params.append(key)
            units.append(parameter.unit)
            default_values[key] = parameter.value

        self.entry_widgets, self.string_vars = create_entries(
            frame=self.entry_frame,
            title="Soil Input Parameters",
            labels=params,
            units=units,
            defaults=default_values,
        )

        self._controller.bind_test_input_fields_to_update_functions(self.string_vars)
        self.setup_mohr_coulomb_controls(params)

    def _create_mohr_options(self, params):
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
