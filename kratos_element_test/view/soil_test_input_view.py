from tkinter import ttk

from PIL import Image, ImageTk
import tkinter as tk

from kratos_element_test.view.ui_constants import (
    TEST_NAME_TO_TYPE,
    HELP_MENU_FONT,
    TEST_IMAGE_FILES,
    TRIAXIAL,
    CRS,
    INPUT_SECTION_FONT,
    INIT_PRESSURE_LABEL,
    MAX_STRAIN_LABEL,
    NUM_STEPS_LABEL,
    DURATION_LABEL,
    FL2_UNIT_LABEL,
    PERCENTAGE_UNIT_LABEL,
    WITHOUT_UNIT_LABEL,
    SECONDS_UNIT_LABEL,
    DIRECT_SHEAR,
    STRAIN_INCREMENT_LABEL,
    STEPS_LABEL,
)
from kratos_element_test.view.ui_logger import log_message
from kratos_element_test.view.ui_utils import _asset_path
import tkinter.font as tkFont


class SoilTestInputView(ttk.Frame):
    def __init__(self, soil_test_input_controller, update_plots_callback, master, **kwargs):
        super().__init__(master, **kwargs)
        self._soil_test_input_controller = soil_test_input_controller
        self.pack(fill="both", expand=True)
        self.test_selector_frame = ttk.Frame(self, padding="5")
        self.test_selector_frame.pack(fill="x", pady=(10, 5))
        self.update_plots_callback = update_plots_callback
        self.test_buttons = {}

        image_paths = {
            name: _asset_path(filename) for name, filename in TEST_IMAGE_FILES.items()
        }

        self.test_images = {}
        for key, path in image_paths.items():
            try:
                img = Image.open(path)
                img_resized = img.resize((85, 85), Image.Resampling.LANCZOS)
                self.test_images[key] = ImageTk.PhotoImage(img_resized)
            except Exception as e:
                log_message(f"Failed to load or resize image: {path} ({e})", "error")
                self.test_images[key] = None

        for test_name in TEST_NAME_TO_TYPE.keys():
            btn = tk.Button(
                self.test_selector_frame,
                text=test_name,
                image=self.test_images[test_name],
                compound="top",
                font=(HELP_MENU_FONT, 8, "bold"),
                width=100,
                height=100,
                relief="raised",
                command=lambda name=test_name: self._switch_test(name),
            )
            btn.pack(side="left", padx=5, pady=5)
            self.test_buttons[test_name] = btn

        self.test_input_frame = ttk.Frame(self, padding="10")
        self.test_input_frame.pack(fill="both", expand=True)

        self._switch_test(TRIAXIAL)

    def _switch_test(self, test_name):
        for name, button in self.test_buttons.items():
            if name == test_name:
                button.config(relief="sunken", bg="SystemButtonFace", state="normal")
            else:
                button.config(relief="raised", bg="SystemButtonFace", state="normal")

        for w in self.test_input_frame.winfo_children():
            w.destroy()

        self._soil_test_input_controller.set_current_test_type(test_name)
        if test_name == TRIAXIAL:
            self.update_plots_callback(num_plots=5)
            ttk.Label(
                self.test_input_frame,
                text="Triaxial Input Data",
                font=(INPUT_SECTION_FONT, 12, "bold"),
            ).pack(anchor="w", padx=5, pady=(5, 0))
            self._add_test_type_dropdown(self.test_input_frame)

            inputs = self._soil_test_input_controller.get_triaxial_inputs()

            input_values = {
                INIT_PRESSURE_LABEL: inputs.initial_effective_cell_pressure,
                MAX_STRAIN_LABEL: inputs.maximum_strain,
                NUM_STEPS_LABEL: inputs.number_of_steps,
                DURATION_LABEL: inputs.duration_in_seconds,
            }
            self.triaxial_widgets, self.triaxial_string_vars = self._create_entries(
                self.test_input_frame,
                "",
                [
                    INIT_PRESSURE_LABEL,
                    MAX_STRAIN_LABEL,
                    NUM_STEPS_LABEL,
                    DURATION_LABEL,
                ],
                [
                    FL2_UNIT_LABEL,
                    PERCENTAGE_UNIT_LABEL,
                    WITHOUT_UNIT_LABEL,
                    SECONDS_UNIT_LABEL,
                ],
                input_values,
            )

            self._soil_test_input_controller.bind_test_input_fields_to_update_functions(
                self.triaxial_string_vars, TRIAXIAL
            )

        elif test_name == DIRECT_SHEAR:
            self.update_plots_callback(num_plots=4)
            ttk.Label(
                self.test_input_frame,
                text="Direct Simple Shear Input Data",
                font=(INPUT_SECTION_FONT, 12, "bold"),
            ).pack(anchor="w", padx=5, pady=(5, 0))
            self._add_test_type_dropdown(self.test_input_frame)

            inputs = self._soil_test_input_controller.get_shear_inputs()

            input_values = {
                INIT_PRESSURE_LABEL: inputs.initial_effective_cell_pressure,
                MAX_STRAIN_LABEL: inputs.maximum_strain,
                NUM_STEPS_LABEL: inputs.number_of_steps,
                DURATION_LABEL: inputs.duration_in_seconds,
            }
            self.shear_widgets, self.shear_string_vars = self._create_entries(
                self.test_input_frame,
                "",
                [
                    INIT_PRESSURE_LABEL,
                    MAX_STRAIN_LABEL,
                    NUM_STEPS_LABEL,
                    DURATION_LABEL,
                ],
                [
                    FL2_UNIT_LABEL,
                    PERCENTAGE_UNIT_LABEL,
                    WITHOUT_UNIT_LABEL,
                    SECONDS_UNIT_LABEL,
                ],
                input_values,
            )

            self._soil_test_input_controller.bind_test_input_fields_to_update_functions(
                self.shear_string_vars, DIRECT_SHEAR
            )

        elif test_name == CRS:
            self.update_plots_callback(num_plots=5)
            ttk.Label(
                self.test_input_frame,
                text="Constant Rate of Strain Input Data",
                font=(INPUT_SECTION_FONT, 12, "bold"),
            ).pack(anchor="w", padx=5, pady=(5, 0))
            tk.Label(
                self.test_input_frame,
                text="(For Strain increment, compression is negative)",
                font=(INPUT_SECTION_FONT, 9),
            ).pack(anchor="w", padx=5, pady=(0, 5))

            self.crs_button_frame = ttk.Frame(self.test_input_frame)
            self.crs_button_frame.pack(fill="x", padx=10, pady=(5, 5))

            add_row_button = ttk.Button(
                self.crs_button_frame, text="Add Row", command=self._add_new_crs_row
            )
            add_row_button.pack(side="left", padx=5)

            self.remove_row_button = ttk.Button(
                self.crs_button_frame,
                text="Remove Row",
                command=self._remove_crs_row,
                state="disabled",
            )
            self.remove_row_button.pack(side="left", padx=5)

            self.crs_table_frame = ttk.Frame(self.test_input_frame)
            self.crs_table_frame.pack(fill="x", padx=10, pady=5)

            self.crs_rows = []

            crs_input = self._soil_test_input_controller.get_crs_inputs()

            for increment in crs_input.strain_increments:
                self._add_crs_row(
                    duration=increment.duration_in_hours,
                    strain_inc=increment.strain_increment,
                    steps=increment.steps,
                )

        log_message(f"{test_name} test selected.", "info")

    def _add_test_type_dropdown(self, parent):
        ttk.Label(
            parent, text="Type of Test:", font=(INPUT_SECTION_FONT, 10, "bold")
        ).pack(anchor="w", padx=5, pady=(5, 2))

        self.test_type_var = tk.StringVar(value="Drained")
        self.test_type_menu = ttk.Combobox(
            parent,
            textvariable=self.test_type_var,
            values=["Drained"],
            state="readonly",
            width=12,
        )
        self.test_type_menu.pack(anchor="w", padx=10, pady=(0, 10))

        def _sync_drainage_from_combobox(*_):
            val = (self.test_type_var.get() or "").strip().lower()
            # self.controller.set_drainage("drained" if val.startswith("drained") else "undrained")

        self.test_type_menu.bind(
            "<<ComboboxSelected>>", lambda e: _sync_drainage_from_combobox()
        )
        _sync_drainage_from_combobox()

    def _add_crs_row(self, duration=1.0, strain_inc=0.0, steps=100):
        row = {}
        string_vars = {}
        row_frame = ttk.Frame(self.crs_table_frame)
        row_frame.pack(fill="x", pady=2)

        default_font = tkFont.nametofont("TkDefaultFont").copy()
        default_font.configure(size=10)

        for label, width, unit, default in zip(
            [DURATION_LABEL, STRAIN_INCREMENT_LABEL, STEPS_LABEL],
            [10, 10, 10],
            ["hours ,", "% ,", ""],
            [duration, strain_inc, steps],
        ):
            string_var = tk.StringVar()
            string_var.set(str(default))
            ttk.Label(row_frame, text=label).pack(side="left", padx=5)
            entry = ttk.Entry(row_frame, width=width, textvariable=string_var)
            entry.pack(side="left", padx=2)
            ttk.Label(row_frame, text=unit).pack(side="left", padx=0)
            row[label] = entry
            string_vars[label] = string_var

        test_input_controller = self._soil_test_input_controller
        current_index = len(self.crs_rows)
        self.crs_rows.append(row)
        test_input_controller.bind_crs_test_input_row_to_update_functions(
            string_vars, current_index
        )

        if len(self.crs_rows) > 1:
            self.remove_row_button.config(state="normal")

    def _add_new_crs_row(self):
        test_input_controller = self._soil_test_input_controller

        test_input_controller.add_crs_strain_increment()
        crs_input = test_input_controller.get_crs_inputs()

        self._add_crs_row(
            duration=crs_input.strain_increments[-1].duration_in_hours,
            strain_inc=crs_input.strain_increments[-1].strain_increment,
            steps=crs_input.strain_increments[-1].steps,
        )

    def _prevent_removal_last_crs_row(self):
        minimum_number_of_rows = 1
        if len(self.crs_rows) <= minimum_number_of_rows:
            self.remove_row_button.config(state="disabled")

    def _remove_crs_row(self):
        self._prevent_removal_last_crs_row()

        if self.crs_rows:
            row = self.crs_rows.pop()
            row_frame = next(iter(row.values())).master
            row_frame.destroy()
        self._soil_test_input_controller.remove_last_crs_strain_increment()

        self._prevent_removal_last_crs_row()

    def _create_entries(self, frame, title, labels, units, defaults):
        widgets = {}
        string_vars = {}
        default_font = tkFont.nametofont("TkDefaultFont").copy()
        default_font.configure(size=10)

        ttk.Label(frame, text=title, font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=5)
        for i, label in enumerate(labels):
            string_var = tk.StringVar()
            string_var.set(defaults.get(label, ""))
            unit = units[i] if i < len(units) else ""
            row = ttk.Frame(frame)
            row.pack(fill="x", padx=10, pady=2)
            ttk.Label(row, text=label, font=default_font).pack(side="left", padx=5)
            entry = ttk.Entry(row, font=default_font, width=20, textvariable=string_var)
            entry.pack(side="left", fill="x", expand=True)
            ttk.Label(row, text=unit, font=default_font).pack(side="left", padx=5)
            widgets[label] = entry
            string_vars[label] = string_var
        return widgets, string_vars

    def validate(self, current_test_type):
        widget_dicts = []
        if current_test_type == TRIAXIAL:
            widget_dicts=[self.triaxial_widgets]
        elif current_test_type==DIRECT_SHEAR:
            widget_dicts=[self.shear_widgets]
        elif current_test_type == CRS:
            widget_dicts=self.crs_rows

        self._validate_entries_are_convertible_to_numbers(widget_dicts)

    @staticmethod
    def _validate_entries_are_convertible_to_numbers(widget_dicts):
        for widget_dict in widget_dicts:
            for key, widget in widget_dict.items():
                try:
                    float(widget.get())
                except ValueError:
                    raise ValueError(f"Could not convert entry to number for '{key}'.")
