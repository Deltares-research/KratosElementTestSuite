# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import threading
import tkinter as tk
import traceback
from tkinter import ttk, scrolledtext

from kratos_element_test.view.log_viewer import LogViewer
from kratos_element_test.view.material_input_view import MaterialInputView
from kratos_element_test.view.plot_viewer import PlotViewer
from kratos_element_test.view.soil_test_input_view import SoilTestInputView
from kratos_element_test.view.ui_logger import log_message, clear_log


class GeotechTestUI(ttk.Frame):
    def __init__(self, root, controller, external_widgets=None):
        self.controller = controller
        super().__init__(root)
        self.pack(side="top", fill="both", expand=True)
        self.root = root
        self._init_frames()

        self.plot_frame = PlotViewer(
            self.controller._result_controller, self, padding="5", width=800, height=600
        )
        self.plot_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.is_running = False
        self.external_widgets = external_widgets if external_widgets else []

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

        self.material_input_view = MaterialInputView(
            self.controller._material_input_controller, self.left_frame, padding="10"
        )
        self.material_input_view.pack(fill="both", expand=True, pady=10)

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

    def _create_input_fields(self):
        for w in self.button_frame.winfo_children():
            w.destroy()

        self.material_input_view.refresh()

        self.soil_test_input_view = SoilTestInputView(
            self.controller._soil_test_input_controller,
            self._init_plot_canvas,
            self.material_input_view,
        )

        clear_log()

        self.run_button = ttk.Button(
            self.button_frame,
            text="Run Calculation",
            command=self._start_simulation_thread,
        )
        self.run_button.pack(pady=5)

    def _run_simulation(self):
        try:
            log_message("Starting calculation... Please wait...", "info")
            self.root.update_idletasks()

            self.soil_test_input_view.validate(self.controller.get_current_test_type())

            success = self.controller.run()

            if success:
                self.plot_frame.draw()
                test_type = self.controller.get_current_test_type()
                log_message(f"{test_type} test completed successfully.", "info")

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
        if hasattr(self, "model_menu"):
            self.model_menu.config(state="disabled")
        # self.c_dropdown.config(state="disabled")
        # self.phi_dropdown.config(state="disabled")
        self._set_widget_state(self.button_frame, "disabled")
        if hasattr(self, "scrollbar"):
            self._original_scroll_cmd = self.scrollbar.cget("command")
            self.scrollbar.config(command=lambda *args: None)
        self.soil_test_input_view.disable_test_type_menu()
        self.scroll_canvas.unbind_all("<MouseWheel>")

    def _enable_gui(self):
        self._set_widget_state(self.left_frame, "normal")

        if hasattr(self, "soil_test_input_view"):
            self.soil_test_input_view.prevent_removal_last_crs_row()

        self.run_button.config(state="normal")

        if hasattr(self, "scrollbar") and hasattr(self, "_original_scroll_cmd"):
            self.scrollbar.config(command=self._original_scroll_cmd)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
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
