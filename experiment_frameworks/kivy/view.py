from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class MyView(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button = Button(text="Generate Graph")
        self.amplitude_input = TextInput(multiline=False, input_filter='float')
        self.frequency_input = TextInput(multiline=False, input_filter='float')
        self.phase_input = TextInput(multiline=False, input_filter='float')
        self.plot_view = Image()
        self.gridLayout = None

    def build(self):
        self.mainLayout = GridLayout(cols = 1)
        self.gridLayout = GridLayout(cols=2)
        self.gridLayout.add_widget(Label(text="Amplitude:"))
        self.gridLayout.add_widget(self.amplitude_input)
        self.gridLayout.add_widget(Label(text="Frequency:"))
        self.gridLayout.add_widget(self.frequency_input)
        self.gridLayout.add_widget(Label(text="Phase:"))
        self.gridLayout.add_widget(self.phase_input)
        self.gridLayout.add_widget(self.button)
        self.mainLayout.add_widget(self.plot_view)
        self.mainLayout.add_widget(self.gridLayout)
        return self.mainLayout
