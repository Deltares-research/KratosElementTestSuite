from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from kratos_element_test.view.ui_constants import INPUT_SECTION_FONT
from kratos_element_test.view.ui_logger import init_log_widget


class LogViewer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=dp(150), **kwargs)

        label = Label(
            text="Log Output:",
            size_hint_y=None,
            height=dp(25),
            bold=True,
            font_size='10sp'
        )
        self.add_widget(label)
        
        scroll_view = ScrollView(size_hint=(1, 1))
        
        self.log_widget = TextInput(
            text="",
            readonly=True,
            multiline=True,
            size_hint_y=None,
            font_name='RobotoMono-Regular',
            font_size='9sp'
        )
        self.log_widget.bind(minimum_height=self.log_widget.setter('height'))
        
        scroll_view.add_widget(self.log_widget)
        self.add_widget(scroll_view)

        init_log_widget(self.log_widget)
