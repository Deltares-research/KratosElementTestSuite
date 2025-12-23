# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import threading
import tkinter as tk
import tkinter.font as tkFont
import traceback
from tkinter import ttk, scrolledtext

from PIL import Image, ImageTk

from kratos_element_test.controller.element_test_controller import ElementTestController
from kratos_element_test.plotters.matplotlib_plotter import MatplotlibPlotter
from kratos_element_test.view.log_viewer import LogViewer
from kratos_element_test.view.plot_viewer import PlotViewer
from kratos_element_test.view.result_registry import register_ui_instance
from kratos_element_test.view.soil_parameter_entries import SoilParameterEntries
from kratos_element_test.view.ui_constants import (
    TRIAXIAL, DIRECT_SHEAR, CRS,
    TEST_NAME_TO_TYPE, TEST_IMAGE_FILES,
    MAX_STRAIN_LABEL, INIT_PRESSURE_LABEL, NUM_STEPS_LABEL, DURATION_LABEL, STRAIN_INCREMENT_LABEL, STEPS_LABEL,
    FL2_UNIT_LABEL, SECONDS_UNIT_LABEL, PERCENTAGE_UNIT_LABEL, WITHOUT_UNIT_LABEL,
    INPUT_SECTION_FONT, HELP_MENU_FONT
)
from kratos_element_test.view.ui_logger import log_message, clear_log
from kratos_element_test.view.ui_utils import _asset_path


class GeotechTestUI(ttk.Frame):
    def __init__(self, root, test_name, dll_path, model_dict, external_widgets=None):
        super().__init__(root)
        self.pack(side="top", fill="both", expand=True)

        self.root = root
        self.test_name = test_name
        self.dll_path = dll_path
        self.model_dict = model_dict
        self.is_linear_elastic = model_dict["model_name"][0].lower() == "linear elastic model"

        self.model_var = tk.StringVar(root)
        self.model_var.set(model_dict["model_name"][0])
        self.current_test = tk.StringVar(value=test_name)
        self.test_input_history = {}

        def _sync_test_type(*_):
            value = self.current_test.get()
            tt = TEST_NAME_TO_TYPE.get(value, "triaxial")
            self.controller.set_test_type(tt)
            self.current_test.trace_add("write", lambda *_: _sync_test_type())
            _sync_test_type()

        self._init_frames()

        self.plot_frame = PlotViewer(self, padding="5", width=800, height=600)
        self.plot_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.is_running = False
        self.external_widgets = external_widgets if external_widgets else []

        self.controller = ElementTestController(
            logger=log_message,
            plotter_factory=lambda axes: MatplotlibPlotter(axes, logger=log_message)
        )

        register_ui_instance(self)
        self._init_dropdown_section()
        self._create_input_fields()

    def _start_simulation_thread(self):
        if self.is_running:
            return
        self.is_running = True
        self._disable_gui()
        threading.Thread(target=self._run_simulation, daemon=True).start()

    def _init_frames(self):
        self.left_panel = ttk.Frame(self, width=555)
        self.left_panel.pack_propagate(False)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)

        self.scrollable_container = ttk.Frame(self.left_panel)
        self.scrollable_container.pack(fill="both", expand=True)

        self.scroll_canvas = tk.Canvas(self.scrollable_container, borderwidth=0, highlightthickness=0)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.scrollable_container, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.left_frame = ttk.Frame(self.scroll_canvas)
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.left_frame, anchor="nw")

        self.left_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.dropdown_frame = ttk.Frame(self.left_frame)
        self.dropdown_frame.pack(fill="x")

        self.param_frame = SoilParameterEntries(self.left_frame, padding="10")
        self.param_frame.pack(fill="both", expand=True, pady=10)

        self.button_frame = ttk.Frame(self.left_panel, padding="10")
        self.button_frame.pack(fill="x", pady=(0, 5))

        self.run_button = ttk.Button(self.button_frame, text="Run Calculation", command=self._start_simulation_thread)
        self.run_button.pack(pady=5, fill="x")

        self._init_log_section()

    def _init_plot_canvas(self, num_plots):
        self.plot_frame.initialize(num_plots)

    def _init_dropdown_section(self):
        ttk.Label(self.dropdown_frame, text="Select a Model:",
                  font=(INPUT_SECTION_FONT, 12, "bold")).pack(anchor="w", padx=5, pady=5)
        self.model_menu = ttk.Combobox(self.dropdown_frame, textvariable=self.model_var,
                                       values=self.model_dict["model_name"], state="readonly")
        self.model_menu.pack(side="top", fill="x", expand=True, padx=5)
        self.model_var.trace("w", lambda *args: self._create_input_fields())

        if self.is_linear_elastic:
            self.model_menu.configure(state="disabled")
        else:
            self.model_menu.configure(state="readonly")

    def _create_input_fields(self):
        for w in self.param_frame.winfo_children() + self.button_frame.winfo_children():
            w.destroy()

        index = self.model_dict["model_name"].index(self.model_var.get())
        params = self.model_dict["param_names"][index]
        units = self.model_dict.get("param_units", [[]])[index]

        default_values = {}
        self.entry_widgets = self._create_entries(self.param_frame, "Soil Input Parameters",
                                                  params, units, default_values)

        self.mohr_checkbox = tk.BooleanVar()
        self.cohesion_var = tk.StringVar(value="3")
        self.phi_var = tk.StringVar(value="4")
        self._create_mohr_options(params)
        if self.is_linear_elastic:
            self.mohr_checkbox_widget.configure(state="disabled")

        self.test_selector_frame = ttk.Frame(self.param_frame, padding="5")
        self.test_selector_frame.pack(fill="x", pady=(10, 5))

        self.test_buttons = {}

        image_paths = {name: _asset_path(filename) for name, filename in TEST_IMAGE_FILES.items()}

        self.test_images = {}
        for key, path in image_paths.items():
            try:
                img = Image.open(path)
                img_resized = img.resize((85, 85), Image.LANCZOS)
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
                command=lambda name=test_name: self._switch_test(name)
            )
            btn.pack(side="left", padx=5, pady=5)
            self.test_buttons[test_name] = btn

        self.test_input_frame = ttk.Frame(self.param_frame, padding="10")
        self.test_input_frame.pack(fill="both", expand=True)

        self._switch_test(TRIAXIAL)

        self.run_button = ttk.Button(self.button_frame, text="Run Calculation", command=self._start_simulation_thread)
        self.run_button.pack(pady=5)

    def _create_entries(self, frame, title, labels, units, defaults):
        widgets = {}

        default_font = tkFont.nametofont("TkDefaultFont").copy()
        default_font.configure(size=10)

        ttk.Label(frame, text=title, font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=5)
        for i, label in enumerate(labels):
            unit = units[i] if i < len(units) else ""
            row = ttk.Frame(frame)
            row.pack(fill="x", padx=10, pady=2)
            ttk.Label(row, text=label, font=default_font).pack(side="left", padx=5)
            entry = ttk.Entry(row, font=default_font, width=20)
            entry.insert(0, defaults.get(label, ""))
            entry.pack(side="left", fill="x", expand=True)
            ttk.Label(row, text=unit, font=default_font).pack(side="left", padx=5)
            widgets[label] = entry
        return widgets

    def _create_mohr_options(self, params):
        self.mohr_frame = ttk.Frame(self.param_frame)
        self.mohr_frame.pack(fill="x", padx=10, pady=5)

        self.mohr_checkbox_widget = ttk.Checkbutton(
            self.mohr_frame,
            text="Mohr-Coulomb Model",
            variable=self.mohr_checkbox,
            command=self._toggle_mohr_options
        )
        self.mohr_checkbox_widget.pack(side="left")

        self.c_label = ttk.Label(self.mohr_frame, text="Indices (1-based): Cohesion")
        self.c_dropdown = ttk.Combobox(self.mohr_frame, textvariable=self.cohesion_var,
                                       values=[str(i+1) for i in range(len(params))], state="readonly", width=2)

        self.phi_label = ttk.Label(self.mohr_frame, text="Friction Angle")
        self.phi_dropdown = ttk.Combobox(self.mohr_frame, textvariable=self.phi_var,
                                         values=[str(i+1) for i in range(len(params))], state="readonly", width=2)

        def _sync_mapping(*_):
            c_idx, phi_idx = self._parse_mc_indices()
            self.controller.set_mohr_mapping(c_idx, phi_idx)

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

            self.controller.set_mohr_enabled(True)
            c_idx, phi_idx = self._parse_mc_indices()
            self.controller.set_mohr_mapping(c_idx, phi_idx)

            for w in widgets:
                w.pack(side="left", padx=5)

        else:
            self.controller.set_mohr_enabled(False)
            self.controller.set_mohr_mapping(None, None)

            for w in widgets:
                w.pack_forget()

    def _switch_test(self, test_name):
        clear_log()
        self.current_test.set(test_name)

        for name, button in self.test_buttons.items():
            if name == test_name:
                button.config(relief="sunken", bg="SystemButtonFace", state="normal")
            else:
                button.config(relief="raised", bg="SystemButtonFace", state="normal")

        for w in self.test_input_frame.winfo_children():
            w.destroy()

        if test_name == TRIAXIAL:
            self._init_plot_canvas(num_plots=5)
            ttk.Label(self.test_input_frame, text="Triaxial Input Data",
                      font=(INPUT_SECTION_FONT, 12, "bold")).pack(anchor="w", padx=5, pady=(5, 0))
            self._add_test_type_dropdown(self.test_input_frame)

            test_input_controller = self.controller._soil_test_input_controller
            inputs = test_input_controller.get_triaxial_inputs()

            input_values = {INIT_PRESSURE_LABEL: inputs.initial_effective_cell_pressure, MAX_STRAIN_LABEL: inputs.maximum_strain,
                        NUM_STEPS_LABEL: inputs.number_of_steps, DURATION_LABEL: inputs.duration}
            self.triaxial_widgets = self._create_entries(
                self.test_input_frame,
                "",
                [INIT_PRESSURE_LABEL, MAX_STRAIN_LABEL, NUM_STEPS_LABEL, DURATION_LABEL],
                [FL2_UNIT_LABEL, PERCENTAGE_UNIT_LABEL, WITHOUT_UNIT_LABEL, SECONDS_UNIT_LABEL],
                input_values
            )

            test_input_controller.bind_widgets_to_handling_functions(self.triaxial_widgets, TRIAXIAL)

        elif test_name == DIRECT_SHEAR:
            self._init_plot_canvas(num_plots=4)
            ttk.Label(self.test_input_frame, text="Direct Simple Shear Input Data",
                      font=(INPUT_SECTION_FONT, 12, "bold")).pack(anchor="w", padx=5, pady=(5, 0))
            self._add_test_type_dropdown(self.test_input_frame)

            test_input_controller = self.controller._soil_test_input_controller
            inputs = test_input_controller.get_shear_inputs()

            input_values = {INIT_PRESSURE_LABEL: inputs.initial_effective_cell_pressure, MAX_STRAIN_LABEL: inputs.maximum_strain,
                            NUM_STEPS_LABEL: inputs.number_of_steps, DURATION_LABEL: inputs.duration}
            self.shear_widgets = self._create_entries(
                self.test_input_frame,
                "",
                [INIT_PRESSURE_LABEL, MAX_STRAIN_LABEL, NUM_STEPS_LABEL, DURATION_LABEL],
                [FL2_UNIT_LABEL, PERCENTAGE_UNIT_LABEL, WITHOUT_UNIT_LABEL, SECONDS_UNIT_LABEL],
                input_values
            )

            test_input_controller.bind_widgets_to_handling_functions(self.shear_widgets, DIRECT_SHEAR)

        elif test_name == CRS:
            self._init_plot_canvas(num_plots=5)
            ttk.Label(self.test_input_frame, text="Constant Rate of Strain Input Data",
                      font=(INPUT_SECTION_FONT, 12, "bold")).pack(anchor="w", padx=5, pady=(5, 0))
            tk.Label(self.test_input_frame, text="(For Strain increment, compression is negative)",
                     font=(INPUT_SECTION_FONT, 9)).pack(anchor="w", padx=5, pady=(0, 5))

            self.crs_button_frame = ttk.Frame(self.test_input_frame)
            self.crs_button_frame.pack(fill="x", padx=10, pady=(5, 5))

            add_row_button = ttk.Button(
                self.crs_button_frame,
                text="Add Row",
                command=self._add_new_crs_row)
            add_row_button.pack(side="left", padx=5)

            self.remove_row_button = ttk.Button(
                self.crs_button_frame,
                text="Remove Row",
                command=self._remove_crs_row,
                state="disabled")
            self.remove_row_button.pack(side="left", padx=5)

            self.crs_table_frame = ttk.Frame(self.test_input_frame)
            self.crs_table_frame.pack(fill="x", padx=10, pady=5)

            self.crs_rows = []

            crs_input = self.controller._soil_test_input_controller.get_crs_inputs()

            for increment in crs_input.strain_increments:
                self._add_crs_row(duration=increment.duration_in_hours, strain_inc=increment.strain_increment, steps=increment.steps)

        log_message(f"{test_name} test selected.", "info")

    def _add_test_type_dropdown(self, parent):
        ttk.Label(parent, text="Type of Test:",
                  font=(INPUT_SECTION_FONT, 10, "bold")).pack(anchor="w", padx=5, pady=(5, 2))

        self.test_type_var = tk.StringVar(value="Drained")
        self.test_type_menu = ttk.Combobox(
            parent,
            textvariable=self.test_type_var,
            values=["Drained"],
            state="readonly",
            width=12
        )
        self.test_type_menu.pack(anchor="w", padx=10, pady=(0, 10))

        def _sync_drainage_from_combobox(*_):
            val = (self.test_type_var.get() or "").strip().lower()
            self.controller.set_drainage("drained" if val.startswith("drained") else "undrained")

        self.test_type_menu.bind("<<ComboboxSelected>>", lambda e: _sync_drainage_from_combobox())
        _sync_drainage_from_combobox()

    def _run_simulation(self):
        try:
            log_message("Starting calculation... Please wait...", "info")
            self.root.update_idletasks()

            material_params = [e.get() for e in self.entry_widgets.values()]
            udsm_number = self.model_dict["model_name"].index(self.model_var.get()) + 1 if self.dll_path else None
            test_type = self.current_test.get()
            tt = TEST_NAME_TO_TYPE.get(test_type, "triaxial")

            if test_type in [TRIAXIAL, DIRECT_SHEAR]:
                widgets = self.triaxial_widgets if test_type == TRIAXIAL else self.shear_widgets
                sigma_init, eps_max, n_steps, duration = self._extract_classic_inputs(widgets)

                self.controller.stage_durations = None
                self.controller.strain_incs = None
                self.controller.step_counts = None

            elif test_type == CRS:
                sigma_init = 0.0
                stage_durations, strain_incs, step_counts = self._extract_staged_inputs()

                eps_max = sum(strain_incs)
                n_steps = sum(step_counts)
                duration = sum(stage_durations)

                if abs(eps_max) >= 100:
                    raise ValueError("Sum of strain increments reaches or exceeds ±100%. Please revise your input.")

                self.controller.stage_durations = stage_durations
                self.controller.strain_incs = strain_incs
                self.controller.step_counts = step_counts

            else:
                raise ValueError(f"Unsupported test type: {test_type}")

            success = self.controller.run(
                axes=self.plot_frame.axes,
                test_type=tt,
                dll_path=self.dll_path or "",
                udsm_number=udsm_number,
                material_parameters=[float(x) for x in material_params],
                sigma_init=sigma_init,
                eps_max=eps_max,
                n_steps=n_steps,
                duration=duration
            )

            if success:
                self.plot_frame.draw()
                log_message(f"{test_type} test completed successfully.", "info")
                if hasattr(self.controller, "latest_results"):
                    self.latest_results = self.controller.latest_results
                self.latest_test_type = tt

        except Exception:
            log_message("An error occurred during simulation:", "error")
            log_message(traceback.format_exc(), "error")
        finally:
            self.root.after(0, self._enable_gui)
            self.is_running = False

    def _enable_run_button(self):
        self.run_button.config(state="normal")
        self.is_running = False

    def _set_widget_state(self, parent, state):
        for child in parent.winfo_children():
            if isinstance(child, ttk.Combobox):
                child.configure(state="readonly")
            elif isinstance(child, (ttk.Entry, tk.Button, ttk.Button, tk.Checkbutton, ttk.Checkbutton)):
                child.configure(state=state)
            elif isinstance(child, scrolledtext.ScrolledText):
                child.config(state=state if state == "normal" else "disabled")
            elif isinstance(child, (ttk.Frame, tk.Frame)):
                self._set_widget_state(child, state)

        for widget in self.external_widgets:
            if isinstance(widget, ttk.Combobox):
                widget.configure(state="readonly" if state == "normal" else "disabled")
            else:
                widget.configure(state=state)

    def _disable_gui(self):
        self._set_widget_state(self.left_frame, "disabled")
        self.model_menu.config(state="disabled")
        self.c_dropdown.config(state="disabled")
        self.phi_dropdown.config(state="disabled")
        self._set_widget_state(self.button_frame, "disabled")
        if hasattr(self, "scrollbar"):
            self._original_scroll_cmd = self.scrollbar.cget("command")
            self.scrollbar.config(command=lambda *args: None)
        if hasattr(self, "test_type_menu") and self.test_type_menu.winfo_exists():
            self.test_type_menu.config(state="disabled")
        self.scroll_canvas.unbind_all("<MouseWheel>")

    def _enable_gui(self):
        self._set_widget_state(self.left_frame, "normal")
        self.run_button.config(state="normal")

        if hasattr(self, "scrollbar") and hasattr(self, "_original_scroll_cmd"):
            self.scrollbar.config(command=self._original_scroll_cmd)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        if self.is_linear_elastic:
            self.mohr_checkbox_widget.configure(state="disabled")
            self.model_menu.configure(state="disabled")
        else:
            self.model_menu.configure(state="readonly")

    def _add_crs_row(self, duration=1.0, strain_inc=0.0, steps=100):
        row = {}
        row_frame = ttk.Frame(self.crs_table_frame)
        row_frame.pack(fill="x", pady=2)

        default_font = tkFont.nametofont("TkDefaultFont").copy()
        default_font.configure(size=10)

        for label, width, unit, default in zip(
                [DURATION_LABEL, STRAIN_INCREMENT_LABEL, STEPS_LABEL],
                [10, 10, 10],
                ["hours ,", "% ,", ""],
                [duration, strain_inc, steps]):
            ttk.Label(row_frame, text=label).pack(side="left", padx=5)
            entry = ttk.Entry(row_frame, width=width)
            entry.insert(0, str(default))
            entry.pack(side="left", padx=2)
            ttk.Label(row_frame, text=unit).pack(side="left", padx=0)
            row[label] = entry

        test_input_controller = self.controller._soil_test_input_controller
        current_index = len(self.crs_rows)
        row[DURATION_LABEL].bind("<FocusOut>", lambda e, idx=current_index: test_input_controller.update_crs_duration(
            new_duration=float(self.crs_rows[idx][DURATION_LABEL].get()), index = idx))
        row[STRAIN_INCREMENT_LABEL].bind("<FocusOut>", lambda e, idx=current_index: test_input_controller.update_crs_strain_increment(
            new_strain_increment=float(self.crs_rows[idx][STRAIN_INCREMENT_LABEL].get()), index = idx))
        row[STEPS_LABEL].bind("<FocusOut>", lambda e, idx=current_index: test_input_controller.update_crs_number_of_steps(
            new_steps=float(self.crs_rows[idx][STEPS_LABEL].get()), index = idx))

        self.crs_rows.append(row)

        if len(self.crs_rows) > 1:
            self.remove_row_button.config(state="normal")

    def _add_new_crs_row(self):
        test_input_controller = self.controller._soil_test_input_controller

        test_input_controller.add_crs_strain_increment()
        crs_input = test_input_controller.get_crs_inputs()

        self._add_crs_row(duration=crs_input.strain_increments[-1].duration_in_hours,
                          strain_inc=crs_input.strain_increments[-1].strain_increment,
                          steps=crs_input.strain_increments[-1].steps)


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
        self.controller._soil_test_input_controller.remove_last_crs_strain_increment()

        self._prevent_removal_last_crs_row()

    def _on_mousewheel(self, event):
        if event.delta > 0:
            first, _ = self.scroll_canvas.yview()
            if first <= 0:
                return
        self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _init_log_section(self):
        self.log_viewer = LogViewer(self.left_panel, padding="5")
        self.log_viewer.pack(fill="x", padx=10, pady=(0, 10))

    def _extract_values_from_rows(self, label, data_type):
        try:
            return [data_type(row[label].get()) for row in self.crs_rows]
        except Exception as e:
            raise ValueError(f"Failed to extract CRS inputs '{label}': {e}")

    def _extract_classic_inputs(self, widgets):
        try:
            sigma_init = float(widgets[INIT_PRESSURE_LABEL].get())
            eps_max = float(widgets[MAX_STRAIN_LABEL].get())
            n_steps = float(widgets[NUM_STEPS_LABEL].get())
            duration = float(widgets[DURATION_LABEL].get())
            return sigma_init, eps_max, n_steps, duration
        except Exception as e:
            raise ValueError(f"Failed to extract classic inputs: {e}")

    def _extract_staged_inputs(self):
        durations = self._extract_values_from_rows(DURATION_LABEL, float)
        strains = self._extract_values_from_rows(STRAIN_INCREMENT_LABEL, float)
        steps = self._extract_values_from_rows(STEPS_LABEL, int)

        durations_sec = [d * 3600 for d in durations]  # convert hours → seconds

        return durations_sec, strains, steps