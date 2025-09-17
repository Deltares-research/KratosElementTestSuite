# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import math
import threading
import traceback
import tkinter as tk
from tkinter import ttk, scrolledtext
import tkinter.font as tkFont
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

from kratos_element_test.ui.element_test_controller import ElementTestController
from kratos_element_test.plotters.matplotlib_plotter import MatplotlibPlotter
from kratos_element_test.ui.ui_logger import init_log_widget, log_message, clear_log
from kratos_element_test.ui.ui_utils import _asset_path
from kratos_element_test.ui.ui_constants import (
    TRIAXIAL, DIRECT_SHEAR, CRS,
    TEST_NAME_TO_TYPE, TEST_IMAGE_FILES,
    MAX_STRAIN_LABEL, INIT_PRESSURE_LABEL, NUM_STEPS_LABEL, DURATION_LABEL,
    FL2_UNIT_LABEL, SECONDS_UNIT_LABEL, PERCENTAGE_UNIT_LABEL, WITHOUT_UNIT_LABEL,
    INPUT_SECTION_FONT, HELP_MENU_FONT
)


class GeotechTestUI:
    def __init__(self, root, parent_frame, test_name, dll_path, model_dict, external_widgets=None):
        self.root = root
        self.parent = parent_frame
        self.test_name = test_name
        self.dll_path = dll_path
        self.model_dict = model_dict
        self.is_linear_elastic = model_dict["model_name"][0].lower() == "linear elastic model"

        self.model_var = tk.StringVar(root)
        self.model_var.set(model_dict["model_name"][0])
        self.current_test = tk.StringVar(value=test_name)

        def _sync_test_type(*_):
            value = self.current_test.get()
            tt = TEST_NAME_TO_TYPE.get(value, "triaxial")
            self.controller.set_test_type(tt)
            self.current_test.trace_add("write", lambda *_: _sync_test_type())
            _sync_test_type()

        self._init_frames()

        self.plot_frame = ttk.Frame(self.parent, padding="5", width=800, height=600)
        self.plot_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.is_running = False
        self.external_widgets = external_widgets if external_widgets else []

        self.controller = ElementTestController(
            logger=log_message,
            plotter_factory=lambda axes: MatplotlibPlotter(axes, logger=log_message)
        )

        self._init_dropdown_section()
        self._create_input_fields()

    def _start_simulation_thread(self):
        if self.is_running:
            return
        self.is_running = True
        self._disable_gui()
        threading.Thread(target=self._run_simulation, daemon=True).start()

    def _init_frames(self):
        self.left_panel = ttk.Frame(self.parent, width=555)
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

        self.param_frame = ttk.Frame(self.left_frame, padding="10")
        self.param_frame.pack(fill="both", expand=True, pady=10)

        self.button_frame = ttk.Frame(self.left_panel, padding="10")
        self.button_frame.pack(fill="x", pady=(0, 5))

        self.run_button = ttk.Button(self.button_frame, text="Run Calculation", command=self._start_simulation_thread)
        self.run_button.pack(pady=5, fill="x")

        self._init_log_section()

    def _init_plot_canvas(self, num_plots):
        self._destroy_existing_plot_canvas()

        self.fig = plt.figure(figsize=(12, 8), dpi=100)
        rows = math.ceil(math.sqrt(num_plots))
        cols = math.ceil(num_plots / rows)

        self.gs = GridSpec(rows, cols, figure=self.fig, wspace=0.4, hspace=0.6)
        self.axes = [self.fig.add_subplot(self.gs[i]) for i in range(num_plots)]
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

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
        default_font.configure(size=11)

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
            self.triaxial_widgets = self._create_entries(
                self.test_input_frame,
                "",
                [INIT_PRESSURE_LABEL, MAX_STRAIN_LABEL, NUM_STEPS_LABEL, DURATION_LABEL],
                [FL2_UNIT_LABEL, PERCENTAGE_UNIT_LABEL, WITHOUT_UNIT_LABEL, SECONDS_UNIT_LABEL],
                {INIT_PRESSURE_LABEL: "100", MAX_STRAIN_LABEL: "20",
                 NUM_STEPS_LABEL: "100", DURATION_LABEL: "1.0"}
            )

        elif test_name == DIRECT_SHEAR:
            self._init_plot_canvas(num_plots=4)
            ttk.Label(self.test_input_frame, text="Direct Simple Shear Input Data",
                      font=(INPUT_SECTION_FONT, 12, "bold")).pack(anchor="w", padx=5, pady=(5, 0))
            self._add_test_type_dropdown(self.test_input_frame)
            self.shear_widgets = self._create_entries(
                self.test_input_frame,
                "",
                [INIT_PRESSURE_LABEL, MAX_STRAIN_LABEL, NUM_STEPS_LABEL, DURATION_LABEL],
                [FL2_UNIT_LABEL, PERCENTAGE_UNIT_LABEL, WITHOUT_UNIT_LABEL, SECONDS_UNIT_LABEL],
                {INIT_PRESSURE_LABEL: "100", MAX_STRAIN_LABEL: "20",
                 NUM_STEPS_LABEL: "100", DURATION_LABEL: "1.0"}
            )

        elif test_name == CRS:
            self._init_plot_canvas(num_plots=5)
            ttk.Label(self.test_input_frame, text="Constant Rate of Strain Input Data",
                      font=(INPUT_SECTION_FONT, 12, "bold")).pack(anchor="w", padx=5, pady=(5, 0))
            self._add_test_type_dropdown(self.test_input_frame)

            self.crs_table_frame = ttk.Frame(self.test_input_frame)
            self.crs_table_frame.pack(fill="x", padx=10, pady=5)

            self.crs_rows = []
            self._add_crs_row()  # start with one row

            ttk.Button(self.test_input_frame, text="Add Row", command=self._add_crs_row).pack(pady=5)

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
            index = self.model_dict["model_name"].index(self.model_var.get()) + 1 if self.dll_path else None
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
                stage_durations, strain_incs, step_counts, eps_max, n_steps, duration = self._extract_staged_inputs()

                self.controller.stage_durations = stage_durations
                self.controller.strain_incs = strain_incs
                self.controller.step_counts = step_counts

            else:
                raise ValueError(f"Unsupported test type: {test_type}")

            self.controller.run(
                axes=self.axes,
                test_type=tt,
                dll_path=self.dll_path or "",
                index=index,
                material_parameters=[float(x) for x in material_params],
                sigma_init=sigma_init,
                eps_max=eps_max,
                n_steps=n_steps,
                duration=duration,
                # stage_durations=stage_durations,
                # strain_incs=strain_incs,
                # step_counts=step_counts
            )

            self.canvas.draw()
            log_message(f"{test_type} test completed successfully.", "info")

        except Exception:
            log_message("An error occurred during simulation:", "error")
            log_message(traceback.format_exc(), "error")
            print(traceback.format_exc())
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
        self.test_type_menu.config(state="disabled")
        self.c_dropdown.config(state="disabled")
        self.phi_dropdown.config(state="disabled")
        self._set_widget_state(self.button_frame, "disabled")
        if hasattr(self, "scrollbar"):
            self._original_scroll_cmd = self.scrollbar.cget("command")
            self.scrollbar.config(command=lambda *args: None)
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

    def _destroy_existing_plot_canvas(self):
        if hasattr(self, "plot_frame") and self.plot_frame.winfo_exists():
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
        self.fig = None
        self.canvas = None
        self.axes = []

    def _add_crs_row(self):
        row = {}
        row_frame = ttk.Frame(self.crs_table_frame)
        row_frame.pack(fill="x", pady=2)

        for label, width, unit in zip(["Duration", "Strain inc.", "Steps"], [10, 15, 8], ["day", "%", ""]):
            ttk.Label(row_frame, text=label).pack(side="left", padx=5)
            entry = ttk.Entry(row_frame, width=width)
            entry.pack(side="left", padx=2)
            ttk.Label(row_frame, text=unit).pack(side="left", padx=5)
            row[label] = entry

        self.crs_rows.append(row)

    def _on_mousewheel(self, event):
        if event.delta > 0:
            first, _ = self.scroll_canvas.yview()
            if first <= 0:
                return
        self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _init_log_section(self):
        self.log_frame = ttk.Frame(self.left_panel, padding="5")
        self.log_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(self.log_frame, text="Log Output:", font=(INPUT_SECTION_FONT, 10, "bold")).pack(anchor="w")
        self.log_widget = scrolledtext.ScrolledText(self.log_frame, height=6, width=40, state="disabled",
                                                    wrap="word", font=("Courier", 9))
        self.log_widget.pack(fill="x", expand=False)

        self.log_widget.bind("<Key>", lambda e: "break")
        self.log_widget.bind("<Button-1>", lambda e: "break")
        self.log_widget.bind("<FocusIn>", lambda e: self.root.focus())

        init_log_widget(self.log_widget)

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
        durations = []
        strains = []
        steps = []

        for row in self.crs_rows:
            try:
                d = float(row["Duration"].get())
                s = float(row["Strain inc."].get())
                n = int(row["Steps"].get())
            except Exception as e:
                raise ValueError(f"Failed to extract CRS inputs: {e}")
            durations.append(d)
            strains.append(s)
            steps.append(n)

        eps_max = sum(strains)
        n_steps = sum(steps)
        duration = sum(durations)
        
        print("[DEBUG] CRS Durations:", durations)
        print("[DEBUG] CRS Steps:", steps)
        print("[DEBUG] CRS Total Duration:", duration)
        print("[DEBUG] CRS Total Steps:", n_steps)

        return durations, strains, steps, eps_max, n_steps, duration
