from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image as KivyImage
from kivy.metrics import dp

from kratos_element_test.view.ui_constants import (
    TEST_NAME_TO_TYPE,
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
from kratos_element_test.view.widget_creation_utils import create_entries


class SoilTestInputView(BoxLayout):
    def __init__(self, soil_test_input_controller, update_plots_callback, master=None, **kwargs):
        # Ignore master parameter for Kivy compatibility
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('spacing', 10)
        kwargs.setdefault('padding', 10)
        super().__init__(**kwargs)
        
        self._soil_test_input_controller = soil_test_input_controller
        self.update_plots_callback = update_plots_callback
        self.test_buttons = {}
        
        # Test selector frame
        self.test_selector_frame = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(5)
        )
        self.add_widget(self.test_selector_frame)
        
        # Create test buttons with images
        for test_name in TEST_NAME_TO_TYPE.keys():
            btn_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(100))
            
            # Try to load image
            try:
                img_path = _asset_path(TEST_IMAGE_FILES[test_name])
                img = KivyImage(source=img_path, size_hint=(1, 0.7))
                btn_layout.add_widget(img)
            except Exception as e:
                log_message(f"Failed to load image: {e}", "error")
            
            btn = Button(
                text=test_name,
                size_hint=(1, 0.3),
                on_press=lambda instance, name=test_name: self._switch_test(name)
            )
            btn_layout.add_widget(btn)
            
            self.test_selector_frame.add_widget(btn_layout)
            self.test_buttons[test_name] = btn
        
        # Test input frame
        self.test_input_frame = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10)
        )
        self.add_widget(self.test_input_frame)
        
        self._switch_test(TRIAXIAL)

    def disable(self):
        if hasattr(self, "test_type_menu"):
            self.test_type_menu.disabled = True

    def _switch_test(self, test_name):
        # Update button colors
        for name, button in self.test_buttons.items():
            if name == test_name:
                button.background_color = (0.2, 0.6, 1, 1)  # Primary color
            else:
                button.background_color = (0.5, 0.5, 0.5, 1)  # Outline color

        # Clear test input frame
        self.test_input_frame.clear_widgets()

        self._soil_test_input_controller.set_current_test_type(test_name)
        
        if test_name == TRIAXIAL:
            self.update_plots_callback(num_plots=5)
            
            title = Label(
                text="Triaxial Input Data",
                size_hint_y=None,
                height=dp(30),
                bold=True,
                font_size='12sp'
            )
            self.test_input_frame.add_widget(title)
            
            self._add_test_type_dropdown()

            inputs = self._soil_test_input_controller.get_triaxial_inputs()

            input_values = {
                INIT_PRESSURE_LABEL: inputs.initial_effective_cell_pressure,
                MAX_STRAIN_LABEL: inputs.maximum_strain,
                NUM_STEPS_LABEL: inputs.number_of_steps,
                DURATION_LABEL: inputs.duration_in_seconds,
            }
            
            self.triaxial_widgets, self.triaxial_callbacks = create_entries(
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

            self._bind_triaxial_inputs()

        elif test_name == DIRECT_SHEAR:
            self.update_plots_callback(num_plots=4)
            
            title = Label(
                text="Direct Simple Shear Input Data",
                size_hint_y=None,
                height=dp(30),
                bold=True,
                font_size='12sp'
            )
            self.test_input_frame.add_widget(title)
            
            self._add_test_type_dropdown()

            inputs = self._soil_test_input_controller.get_shear_inputs()

            input_values = {
                INIT_PRESSURE_LABEL: inputs.initial_effective_cell_pressure,
                MAX_STRAIN_LABEL: inputs.maximum_strain,
                NUM_STEPS_LABEL: inputs.number_of_steps,
                DURATION_LABEL: inputs.duration_in_seconds,
            }
            
            self.shear_widgets, self.shear_callbacks = create_entries(
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

            self._bind_shear_inputs()

        elif test_name == CRS:
            self.update_plots_callback(num_plots=5)
            
            title = Label(
                text="Constant Rate of Strain Input Data",
                size_hint_y=None,
                height=dp(30),
                bold=True,
                font_size='12sp'
            )
            self.test_input_frame.add_widget(title)
            
            subtitle = Label(
                text="(For Strain increment, compression is negative)",
                size_hint_y=None,
                height=dp(20),
                font_size='9sp'
            )
            self.test_input_frame.add_widget(subtitle)

            self.crs_button_frame = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=dp(5)
            )
            self.test_input_frame.add_widget(self.crs_button_frame)

            add_row_button = Button(
                text="Add Row",
                on_press=lambda x: self._add_new_crs_row()
            )
            self.crs_button_frame.add_widget(add_row_button)

            self.remove_row_button = Button(
                text="Remove Row",
                disabled=True,
                on_press=lambda x: self._remove_crs_row()
            )
            self.crs_button_frame.add_widget(self.remove_row_button)

            self.crs_table_frame = BoxLayout(
                orientation='vertical',
                spacing=dp(5)
            )
            self.test_input_frame.add_widget(self.crs_table_frame)

            self.crs_rows = []

            crs_input = self._soil_test_input_controller.get_crs_inputs()

            for increment in crs_input.strain_increments:
                self._add_crs_row(
                    duration=increment.duration_in_hours,
                    strain_inc=increment.strain_increment,
                    steps=increment.steps,
                )

        log_message(f"{test_name} test selected.", "info")

    def _add_test_type_dropdown(self):
        label = Label(
            text="Type of Test:",
            size_hint_y=None,
            height=dp(25),
            bold=True,
            font_size='10sp'
        )
        self.test_input_frame.add_widget(label)

        self.test_type_menu = Spinner(
            text="Drained",
            values=["Drained"],
            size_hint_y=None,
            height=dp(35)
        )
        self.test_input_frame.add_widget(self.test_type_menu)

        self._soil_test_input_controller.bind_drainage_combo_box(self.test_type_menu)

    def _bind_triaxial_inputs(self):
        """Bind triaxial input fields to controller update functions"""
        for label, entry in self.triaxial_widgets.items():
            if label == INIT_PRESSURE_LABEL:
                entry.bind(text=lambda inst, val: self._soil_test_input_controller.update_triaxial_pressure(val))
            elif label == MAX_STRAIN_LABEL:
                entry.bind(text=lambda inst, val: self._soil_test_input_controller.update_triaxial_strain(val))
            elif label == NUM_STEPS_LABEL:
                entry.bind(text=lambda inst, val: self._soil_test_input_controller.update_triaxial_steps(val))
            elif label == DURATION_LABEL:
                entry.bind(text=lambda inst, val: self._soil_test_input_controller.update_triaxial_duration(val))

    def _bind_shear_inputs(self):
        """Bind shear input fields to controller update functions"""
        for label, entry in self.shear_widgets.items():
            if label == INIT_PRESSURE_LABEL:
                entry.bind(text=lambda inst, val: self._soil_test_input_controller.update_shear_pressure(val))
            elif label == MAX_STRAIN_LABEL:
                entry.bind(text=lambda inst, val: self._soil_test_input_controller.update_shear_strain(val))
            elif label == NUM_STEPS_LABEL:
                entry.bind(text=lambda inst, val: self._soil_test_input_controller.update_shear_steps(val))
            elif label == DURATION_LABEL:
                entry.bind(text=lambda inst, val: self._soil_test_input_controller.update_shear_duration(val))

    def _add_crs_row(self, duration=1.0, strain_inc=0.0, steps=100):
        row = {}
        row_frame = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5)
        )

        for label_text, default, unit in [
            (DURATION_LABEL, duration, "hours ,"),
            (STRAIN_INCREMENT_LABEL, strain_inc, "% ,"),
            (STEPS_LABEL, steps, "")
        ]:
            lbl = Label(text=label_text, size_hint_x=0.3, font_size='10sp')
            row_frame.add_widget(lbl)
            
            entry = TextInput(
                text=str(default),
                multiline=False,
                size_hint_x=0.3,
                font_size='10sp'
            )
            row_frame.add_widget(entry)
            
            unit_lbl = Label(text=unit, size_hint_x=0.1, font_size='10sp')
            row_frame.add_widget(unit_lbl)
            
            row[label_text] = entry

        current_index = len(self.crs_rows)
        self.crs_rows.append(row)
        self.crs_table_frame.add_widget(row_frame)

        # Bind to controller
        self._bind_crs_row(row, current_index)

        if len(self.crs_rows) > 1:
            self.remove_row_button.disabled = False

    def _bind_crs_row(self, row, index):
        """Bind CRS row inputs to controller"""
        row[DURATION_LABEL].bind(
            text=lambda inst, val: self._soil_test_input_controller.update_crs_duration(index, val)
        )
        row[STRAIN_INCREMENT_LABEL].bind(
            text=lambda inst, val: self._soil_test_input_controller.update_crs_strain(index, val)
        )
        row[STEPS_LABEL].bind(
            text=lambda inst, val: self._soil_test_input_controller.update_crs_steps(index, val)
        )

    def _add_new_crs_row(self):
        self._soil_test_input_controller.add_crs_strain_increment()
        crs_input = self._soil_test_input_controller.get_crs_inputs()

        self._add_crs_row(
            duration=crs_input.strain_increments[-1].duration_in_hours,
            strain_inc=crs_input.strain_increments[-1].strain_increment,
            steps=crs_input.strain_increments[-1].steps,
        )

    def _remove_crs_row(self):
        if len(self.crs_rows) <= 1:
            self.remove_row_button.disabled = True
            return

        if self.crs_rows:
            row = self.crs_rows.pop()
            # Find and remove the row's parent frame from crs_table_frame
            for widget in self.crs_table_frame.children:
                if any(entry.parent == widget for entry in row.values()):
                    self.crs_table_frame.remove_widget(widget)
                    break
                    
        self._soil_test_input_controller.remove_last_crs_strain_increment()

        if len(self.crs_rows) <= 1:
            self.remove_row_button.disabled = True

    def validate(self, current_test_type):
        widget_dicts = []
        if current_test_type == TRIAXIAL:
            widget_dicts = [self.triaxial_widgets]
        elif current_test_type == DIRECT_SHEAR:
            widget_dicts = [self.shear_widgets]
        elif current_test_type == CRS:
            widget_dicts = self.crs_rows

        self._validate_entries_are_convertible_to_numbers(widget_dicts)

    @staticmethod
    def _validate_entries_are_convertible_to_numbers(widget_dicts):
        for widget_dict in widget_dicts:
            for key, widget in widget_dict.items():
                try:
                    float(widget.text)
                except ValueError:
                    raise ValueError(f"Could not convert entry to number for '{key}'.")
