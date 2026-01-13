# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import threading
import traceback
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.metrics import dp

from kratos_element_test.view.log_viewer import LogViewer
from kratos_element_test.view.plot_viewer import PlotViewer
from kratos_element_test.view.soil_parameter_entries import SoilParameterEntries
from kratos_element_test.view.soil_test_input_view import SoilTestInputView
from kratos_element_test.view.ui_constants import INPUT_SECTION_FONT
from kratos_element_test.view.ui_logger import log_message, clear_log
from kratos_element_test.view.widget_creation_utils import create_entries


class GeotechTestUI(BoxLayout):
    def __init__(
        self, root, test_name, dll_path, model_dict, controller, external_widgets=None
    ):
        super().__init__(orientation='horizontal')
        self.controller = controller
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

        self.model_var_value = model_dict["model_name"][0]
        self.test_input_history = {}

        self._init_frames()

        self.plot_frame = PlotViewer(self.controller._result_controller)
        self.add_widget(self.plot_frame)

        self.is_running = False
        self.external_widgets = external_widgets if external_widgets else []

        self._init_dropdown_section()
        self._create_input_fields()

    def _start_simulation_thread(self):
        if self.is_running:
            return
        self.is_running = True
        self._disable_gui()
        threading.Thread(target=self._run_simulation, daemon=True).start()

    def _init_frames(self):
        self.left_panel = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=dp(10), padding=dp(10))
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        scroll_content.bind(minimum_height=scroll_content.setter('height'))
        
        self.dropdown_frame = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        scroll_content.add_widget(self.dropdown_frame)

        self.param_frame = SoilParameterEntries()
        scroll_content.add_widget(self.param_frame)

        scroll_view.add_widget(scroll_content)
        self.left_panel.add_widget(scroll_view)

        self.button_frame = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60), spacing=dp(5))
        self.run_button = Button(text="Run Calculation", on_press=lambda x: self._start_simulation_thread())
        self.button_frame.add_widget(self.run_button)
        self.left_panel.add_widget(self.button_frame)

        self._init_log_section()
        self.add_widget(self.left_panel)

    def _init_plot_canvas(self, num_plots):
        self.plot_frame.initialize(num_plots)

    def _init_dropdown_section(self):
        from kivy.uix.label import Label
        label = Label(text="Select a Model:", size_hint_y=None, height=dp(30), bold=True, font_size='12sp')
        self.dropdown_frame.add_widget(label)
        
        self.model_menu = Spinner(
            text=self.model_var_value,
            values=self.model_dict["model_name"],
            size_hint_y=None,
            height=dp(40)
        )
        self.model_menu.bind(text=lambda inst, val: self._create_input_fields())
        self.dropdown_frame.add_widget(self.model_menu)

        if self.is_linear_elastic or self.is_mohr_coulomb:
            self.model_menu.disabled = True

    def _create_input_fields(self):
        self.param_frame.clear_widgets()
        self.button_frame.clear_widgets()

        index = self.model_dict["model_name"].index(self.model_menu.text)
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

        self.run_button = Button(text="Run Calculation", on_press=lambda x: self._start_simulation_thread())
        self.button_frame.add_widget(self.run_button)

    def _create_mohr_options(self, params):
        from kivy.uix.checkbox import CheckBox
        from kivy.uix.label import Label
        
        self.mohr_frame = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(5))
        self.param_frame.add_widget(self.mohr_frame)

        self.mohr_checkbox_widget = CheckBox(active=self.mohr_checkbox_value)
        self.mohr_checkbox_widget.bind(active=lambda inst, val: self._toggle_mohr_options())
        self.mohr_frame.add_widget(Label(text="Mohr-Coulomb Model"))
        self.mohr_frame.add_widget(self.mohr_checkbox_widget)

        self.c_label = Label(text="Indices (1-based): Cohesion")
        self.c_dropdown = Spinner(
            text=self.cohesion_var_value,
            values=[str(i + 1) for i in range(len(params))],
            size_hint_x=0.2
        )

        self.phi_label = Label(text="Friction Angle")
        self.phi_dropdown = Spinner(
            text=self.phi_var_value,
            values=[str(i + 1) for i in range(len(params))],
            size_hint_x=0.2
        )

        def _sync_mapping(*_):
            c_idx, phi_idx = self._parse_mc_indices()
            self.controller.set_mohr_mapping(c_idx, phi_idx)

        self.c_dropdown.bind(text=_sync_mapping)
        self.phi_dropdown.bind(text=_sync_mapping)
        _sync_mapping()

    def _parse_mc_indices(self):
        try:
            c_idx = int(self.c_dropdown.text) if self.c_dropdown.text else None
            phi_idx = int(self.phi_dropdown.text) if self.phi_dropdown.text else None
        except (ValueError, AttributeError):
            c_idx, phi_idx = None, None
        return c_idx, phi_idx

    def _toggle_mohr_options(self):
        if self.mohr_checkbox_widget.active:
            self.controller.set_mohr_enabled(True)
            c_idx, phi_idx = self._parse_mc_indices()
            self.controller.set_mohr_mapping(c_idx, phi_idx)
            if self.c_label not in self.mohr_frame.children:
                self.mohr_frame.add_widget(self.c_label)
                self.mohr_frame.add_widget(self.c_dropdown)
                self.mohr_frame.add_widget(self.phi_label)
                self.mohr_frame.add_widget(self.phi_dropdown)
        else:
            self.controller.set_mohr_enabled(False)
            self.controller.set_mohr_mapping(None, None)
            for w in [self.c_label, self.c_dropdown, self.phi_label, self.phi_dropdown]:
                if w in self.mohr_frame.children:
                    self.mohr_frame.remove_widget(w)

    def setup_mohr_coulomb_controls(self, params):
        self.mohr_checkbox_value = False
        self.cohesion_var_value = "3"
        self.phi_var_value = "4"
        self._create_mohr_options(params)

        if self.is_linear_elastic:
            self.controller.set_mohr_enabled(False)
            self.controller.set_mohr_mapping(None, None)
            self.param_frame.remove_widget(self.mohr_frame)
        elif self.is_mohr_coulomb:
            self.controller.set_mohr_enabled(True)
            c_idx, phi_idx = self._parse_mc_indices()
            self.controller.set_mohr_mapping(c_idx, phi_idx)
            self.param_frame.remove_widget(self.mohr_frame)
        else:
            self.mohr_checkbox_widget.disabled = False

    def _run_simulation(self):
        try:
            log_message("Starting calculation... Please wait...", "info")

            self.soil_test_input_view.validate(self.controller.get_current_test_type())
            material_params = [e.text for e in self.entry_widgets.values()]
            udsm_number = (
                self.model_dict["model_name"].index(self.model_menu.text) + 1
                if self.dll_path
                else None
            )

            success = self.controller.run(
                model_name=self.model_menu.text,
                dll_path=self.dll_path or "",
                udsm_number=udsm_number,
                material_parameters=[float(x) for x in material_params],
            )

            if success:
                self.plot_frame.draw()
                test_type = self.controller.get_current_test_type()
                log_message(f"{test_type} test completed successfully.", "info")

        except Exception:
            log_message("An error occurred during simulation:", "error")
            log_message(traceback.format_exc(), "error")
        finally:
            Clock.schedule_once(lambda dt: self._enable_gui(), 0)
            self.is_running = False

    def _enable_run_button(self):
        self.run_button.config(state="normal")
        self.is_running = False

    def _set_widget_state(self, parent, enabled):
        from kivy.uix.textinput import TextInput
        for child in parent.children:
            if isinstance(child, (Button, TextInput, Spinner)):
                child.disabled = not enabled
            elif isinstance(child, BoxLayout):
                self._set_widget_state(child, enabled)
        for widget in self.external_widgets:
            widget.disabled = not enabled

    def _disable_gui(self):
        self._set_widget_state(self.left_panel, False)
        self.model_menu.disabled = True
        if hasattr(self, 'c_dropdown'):
            self.c_dropdown.disabled = True
            self.phi_dropdown.disabled = True
        self.soil_test_input_view.disable()

    def _enable_gui(self):
        self._set_widget_state(self.left_panel, True)
        self.run_button.disabled = False
        if self.is_linear_elastic or self.is_mohr_coulomb:
            if hasattr(self, 'mohr_frame') and self.mohr_frame in self.param_frame.children:
                self.param_frame.remove_widget(self.mohr_frame)
            self.model_menu.disabled = True
        else:
            self.model_menu.disabled = False

    def _init_log_section(self):
        self.log_viewer = LogViewer()
        self.left_panel.add_widget(self.log_viewer)
