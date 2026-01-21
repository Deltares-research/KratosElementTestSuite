# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import threading
import tkinter as tk
import traceback
from tkinter import ttk, scrolledtext

from kratos_element_test.controller.element_test_controller import ElementTestController
from kratos_element_test.plotters.matplotlib_plotter import MatplotlibPlotter
from kratos_element_test.view.log_viewer import LogViewer
from kratos_element_test.view.plot_viewer import PlotViewer
from kratos_element_test.view.result_registry import register_ui_instance
from kratos_element_test.view.soil_parameter_entries import SoilParameterEntries
from kratos_element_test.view.soil_test_input_view import SoilTestInputView
from kratos_element_test.view.ui_constants import TEST_NAME_TO_TYPE, INPUT_SECTION_FONT
from kratos_element_test.view.ui_logger import log_message, clear_log
from kratos_element_test.view.widget_creation_utils import create_entries
from kratos_element_test.view.ui_utils import asset_path


class GeotechTestUI(ttk.Frame):
    def __init__(self, root, test_name, dll_path, model_dict, external_widgets=None):
        super().__init__(root)
        self.pack(side="top", fill="both", expand=True)
        self.root = root
        self.test_name = test_name
        self.dll_path = dll_path
        self.model_dict = model_dict
        self.is_linear_elastic = (
            model_dict["model_name"][0].lower() == "linear elastic model"
        )
        self.is_mohr_coulomb = (
            model_dict["model_name"][0].lower() == "mohr-coulomb model"
        )

        self.model_var = tk.StringVar(root)
        self.model_var.set(model_dict["model_name"][0])
        self.test_input_history = {}

        self._init_frames()

        self.plot_frame = PlotViewer(self, padding="5", width=800, height=600)
        self.plot_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.is_running = False
        self.external_widgets = external_widgets if external_widgets else []

        self.controller = ElementTestController(
            logger=log_message,
            plotter_factory=lambda axes: MatplotlibPlotter(axes, logger=log_message),
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

        self.scroll_canvas = tk.Canvas(
            self.scrollable_container, borderwidth=0, highlightthickness=0
        )
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(
            self.scrollable_container,
            orient="vertical",
            command=self.scroll_canvas.yview,
        )
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.left_frame = ttk.Frame(self.scroll_canvas)
        self.canvas_window = self.scroll_canvas.create_window(
            (0, 0), window=self.left_frame, anchor="nw"
        )

        self.left_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(
                scrollregion=self.scroll_canvas.bbox("all")
            ),
        )
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.dropdown_frame = ttk.Frame(self.left_frame)
        self.dropdown_frame.pack(fill="x")

        self.param_frame = SoilParameterEntries(self.left_frame, padding="10")
        self.param_frame.pack(fill="both", expand=True, pady=10)

        self.button_frame = ttk.Frame(self.left_panel, padding="10")
        self.button_frame.pack(fill="x", pady=(0, 5))

        self.run_button = ttk.Button(
            self.button_frame,
            text="Run Calculation",
            command=self._start_simulation_thread,
        )
        self.run_button.pack(pady=5, fill="x")

        self._init_log_section()

    def _init_plot_canvas(self, num_plots):
        self.plot_frame.initialize(num_plots)

    def _init_dropdown_section(self):
        ttk.Label(
            self.dropdown_frame,
            text="Select a Model:",
            font=(INPUT_SECTION_FONT, 12, "bold"),
        ).pack(anchor="w", padx=5, pady=5)
        self.model_menu = ttk.Combobox(
            self.dropdown_frame,
            textvariable=self.model_var,
            values=self.model_dict["model_name"],
            state="readonly",
        )
        self.model_menu.pack(side="top", fill="x", expand=True, padx=5)
        self.model_var.trace("w", lambda *args: self._create_input_fields())

        if self.is_linear_elastic or self.is_mohr_coulomb:
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
        # For now the string_vars are not used yet, but they'll be useful for adding a trace
        # later (similar to the test input fields)
        self.entry_widgets, string_vars = create_entries(
            self.param_frame, "Soil Input Parameters", params, units, default_values
        )

        self.setup_mohr_coulomb_controls(params)

        self.soil_test_input_view = SoilTestInputView(
            self.controller._soil_test_input_controller,
            self._init_plot_canvas,
            self.param_frame,
        )

        clear_log()

        self.run_button = ttk.Button(
            self.button_frame,
            text="Run Calculation",
            command=self._start_simulation_thread,
        )
        self.run_button.pack(pady=5)

    def _create_mohr_options(self, params):
        self.mohr_frame = ttk.Frame(self.param_frame)
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

    def setup_mohr_coulomb_controls(self, params):
        self.mohr_checkbox = tk.BooleanVar()
        self.cohesion_var = tk.StringVar(value="3")
        self.phi_var = tk.StringVar(value="4")
        self._create_mohr_options(params)

        if self.is_linear_elastic:
            self.controller.set_mohr_enabled(False)
            self.controller.set_mohr_mapping(None, None)
            self.mohr_frame.pack_forget()

        elif self.is_mohr_coulomb:
            self.controller.set_mohr_enabled(True)

            c_idx, phi_idx = self._parse_mc_indices()
            self.controller.set_mohr_mapping(c_idx, phi_idx)

            self.mohr_frame.pack_forget()

        else:
            self.mohr_checkbox_widget.configure(state="normal")

    def _run_simulation(self):
        try:
            log_message("Starting calculation... Please wait...", "info")
            self.root.update_idletasks()

            self.soil_test_input_view.validate(self.controller.get_current_test_type())
            material_params = [e.get() for e in self.entry_widgets.values()]
            udsm_number = (
                self.model_dict["model_name"].index(self.model_var.get()) + 1
                if self.dll_path
                else None
            )

            success = self.controller.run(
                axes=self.plot_frame.axes,
                model_name=self.model_var.get(),
                dll_path=self.dll_path or "",
                udsm_number=udsm_number,
                material_parameters=[float(x) for x in material_params],
            )

            if success:
                self.plot_frame.draw()
                test_type = self.controller.get_current_test_type()
                log_message(f"{test_type} test completed successfully.", "info")
                if hasattr(self.controller, "latest_results"):
                    self.latest_results = self.controller.latest_results
                self.latest_test_type = TEST_NAME_TO_TYPE.get(test_type, "triaxial")

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
            elif isinstance(
                child,
                (ttk.Entry, tk.Button, ttk.Button, tk.Checkbutton, ttk.Checkbutton),
            ):
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
        self.soil_test_input_view.disable_test_type_menu()
        self.scroll_canvas.unbind_all("<MouseWheel>")

    def _enable_gui(self):
        self._set_widget_state(self.left_frame, "normal")
        self.run_button.config(state="normal")

        if hasattr(self, "scrollbar") and hasattr(self, "_original_scroll_cmd"):
            self.scrollbar.config(command=self._original_scroll_cmd)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        if self.is_linear_elastic or self.is_mohr_coulomb:
            self.mohr_frame.pack_forget()
            self.model_menu.configure(state="disabled")
        else:
            self.model_menu.configure(state="readonly")

    def _on_mousewheel(self, event):
        if event.delta > 0:
            first, _ = self.scroll_canvas.yview()
            if first <= 0:
                return
        self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _init_log_section(self):
        self.log_viewer = LogViewer(self.left_panel, padding="5")
        self.log_viewer.pack(fill="x", padx=10, pady=(0, 10))
