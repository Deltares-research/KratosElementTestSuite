from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class MyView(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button = Button(text="Generate Graph")
        self.amplitude_input = TextInput(multiline=False, input_filter='float')
        self.gridLayout = None

    def build(self):
        self.gridLayout = GridLayout(cols=2)
        self.gridLayout.add_widget(Label(text="Amplitude:"))
        self.gridLayout.add_widget(self.amplitude_input)
        self.gridLayout.add_widget(self.button)
        return self.gridLayout
