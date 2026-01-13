# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from pathlib import Path
from platformdirs import user_data_dir

from kratos_element_test.controller.element_test_controller import ElementTestController
from kratos_element_test.plotters.matplotlib_plotter import MatplotlibPlotter
from kratos_element_test.view.ui_builder import GeotechTestUI
from kratos_element_test.view.ui_utils import _asset_path
from kratos_element_test.view.ui_constants import (APP_TITLE, APP_VERSION, APP_NAME, APP_AUTHOR, SELECT_UDSM,
                                                  LINEAR_ELASTIC, MOHR_COULOMB)
from kratos_element_test.view.ui_logger import log_message

data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
data_dir.mkdir(parents=True, exist_ok=True)
LICENSE_FLAG_PATH = data_dir / "license_accepted.flag"


class MainUI(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = f"{APP_TITLE} - {APP_VERSION}"
        self.main_frame = None
        self.controller = None
        self.model_source_spinner = None
        self.last_model_source = LINEAR_ELASTIC

    def build(self):
        if not os.path.exists(LICENSE_FLAG_PATH):
            self.show_license_agreement()
        
        self.controller = ElementTestController(
            logger=log_message,
            plotter_factory=lambda axes: MatplotlibPlotter(axes, logger=log_message, line_color='#3498db')
        )

        root_layout = BoxLayout(orientation='vertical')
        
        # Top frame with model selector
        top_frame = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=dp(10))
        self.model_source_spinner = Spinner(
            text="Select Model Source",
            values=[SELECT_UDSM, LINEAR_ELASTIC, MOHR_COULOMB],
            size_hint_x=0.3
        )
        self.model_source_spinner.bind(text=self.handle_model_source_selection)
        top_frame.add_widget(self.model_source_spinner)
        root_layout.add_widget(top_frame)
        
        # Main content area (will be populated by model selection)
        self.content_area = BoxLayout(orientation='vertical')
        root_layout.add_widget(self.content_area)
        
        return root_layout

    def handle_model_source_selection(self, spinner, text):
        if text == SELECT_UDSM:
            self.load_dll()
        elif text == LINEAR_ELASTIC:
            self.load_linear_elastic()
        elif text == MOHR_COULOMB:
            self.load_mohr_coulomb()

    def load_dll(self):
        # For POC, just show message that file dialog would open
        popup = Popup(title='Info',
                     content=Label(text='File dialog would open here to select DLL\n(use plyer.filechooser)'),
                     size_hint=(0.6, 0.4))
        popup.open()
        self.model_source_spinner.text = self.last_model_source

    def load_linear_elastic(self):
        self.last_model_source = LINEAR_ELASTIC
        model_dict = {
            "model_name": [LINEAR_ELASTIC],
            "num_params": [2],
            "param_names": [["Young's Modulus", "Poisson's Ratio"]],
            "param_units": [["kN/m²", "–"]]
        }
        self._load_model(model_dict, None)

    def load_mohr_coulomb(self):
        self.last_model_source = MOHR_COULOMB
        model_dict = {
            "model_name": [MOHR_COULOMB],
            "num_params": [4],
            "param_names": [[
                "Young's Modulus",
                "Poisson's Ratio",
                "Cohesion",
                "Friction Angle",
                "Tensile Strength",
                "Dilatancy Angle",
            ]],
            "param_units": [["kN/m²", "-", "kN/m²", "deg", "kN/m²", "deg"]],
        }
        self._load_model(model_dict, None)

    def _load_model(self, model_dict, dll_path):
        self.content_area.clear_widgets()
        self.main_frame = GeotechTestUI(
            self.root, 
            test_name="Triaxial", 
            dll_path=dll_path, 
            model_dict=model_dict,
            controller=self.controller, 
            external_widgets=[self.model_source_spinner]
        )
        self.content_area.add_widget(self.main_frame)

    def show_license_agreement(self, readonly=False):
        license_file_path = _asset_path("license.txt")
        try:
            with open(license_file_path, "r", encoding="utf-8") as f:
                license_text = f.read()
        except Exception as e:
            popup = Popup(title='Error',
                         content=Label(text=f"Could not load license file: {e}"),
                         size_hint=(0.6, 0.4))
            popup.open()
            return

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text="Pre-Release Software License Agreement", bold=True, size_hint_y=None, height=dp(30)))
        content.add_widget(Label(text="Please review and accept the agreement to continue.", size_hint_y=None, height=dp(30)))
        
        scroll = ScrollView()
        text_area = TextInput(text=license_text, readonly=True, multiline=True)
        scroll.add_widget(text_area)
        content.add_widget(scroll)

        if not readonly:
            button_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            accept_btn = Button(text="Accept")
            decline_btn = Button(text="Decline")
            
            def accept_license(*args):
                try:
                    with open(LICENSE_FLAG_PATH, "w") as f:
                        f.write("ACCEPTED")
                    license_popup.dismiss()
                except Exception as e:
                    print(f"Error saving license: {e}")
            
            def decline_license(*args):
                import sys
                sys.exit(0)
            
            accept_btn.bind(on_press=accept_license)
            decline_btn.bind(on_press=decline_license)
            button_box.add_widget(accept_btn)
            button_box.add_widget(decline_btn)
            content.add_widget(button_box)

        license_popup = Popup(title='License Agreement', content=content, size_hint=(0.9, 0.9))
        if not readonly:
            license_popup.bind(on_dismiss=lambda x: decline_license())
        license_popup.open()

    def show_about_window(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(Label(text=APP_TITLE, bold=True, font_size='14sp'))
        content.add_widget(Label(text=APP_VERSION, font_size='12sp'))
        content.add_widget(Label(text="Powered by: Kratos & Deltares", font_size='12sp'))
        content.add_widget(Label(text="Contact: kratos@deltares.nl", font_size='12sp'))
        
        close_btn = Button(text="Close", size_hint_y=None, height=dp(50))
        about_popup = Popup(title='About', content=content, size_hint=(0.6, 0.6))
        close_btn.bind(on_press=about_popup.dismiss)
        content.add_widget(close_btn)
        about_popup.open()

    def create_menu(self):
        """Legacy method for compatibility"""
        self.run()


if __name__ == "__main__":
    ui = MainUI()
    ui.run()
