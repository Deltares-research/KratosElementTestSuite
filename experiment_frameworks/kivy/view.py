from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt


class MyView(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button = Button(text="Generate Graph", size_hint=(1, None), height=dp(40),
                             background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1), font_size=18)
        self.amplitude_input = TextInput(multiline=False, input_filter='float', size_hint=(1, None),
                                         height=dp(32), padding=[dp(8), dp(8), dp(8), dp(8)],
                                         background_color=(0.97, 0.97, 0.97, 1))
        self.frequency_input = TextInput(multiline=False, input_filter='float', size_hint=(1, None),
                                         height=dp(32), padding=[dp(8), dp(8), dp(8), dp(8)],
                                         background_color=(0.97, 0.97, 0.97, 1))
        self.phase_input = TextInput(multiline=False, input_filter='float', size_hint=(1, None),
                                     height=dp(32), padding=[dp(8), dp(8), dp(8), dp(8)],
                                     background_color=(0.97, 0.97, 0.97, 1))
        # Create a matplotlib figure and canvas
        self.fig, self.ax = plt.subplots()

        self.plot_canvas = FigureCanvasKivyAgg(self.fig)

    def display_data(self, x, y):
        self.ax.clear()
        self.ax.set_title('Example Sine Wave')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('sin(x)')
        self.ax.legend()
        self.ax.plot(x, y, label='sin(x)', color='royalblue', linewidth=2)
        self.plot_canvas.draw()

    def build(self):
        Window.clearcolor = (0.98, 0.98, 1, 1)
        mainLayout = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(18))
        # Plot area
        plot_anchor = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(1, 0.6))
        plot_anchor.add_widget(self.plot_canvas)
        mainLayout.add_widget(plot_anchor)
        # Input area
        input_card = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12), size_hint=(1, 0.4))
        gridLayout = GridLayout(cols=2, spacing=dp(10), size_hint=(1, None))
        gridLayout.bind(minimum_height=gridLayout.setter('height'))
        gridLayout.add_widget(Label(text="Amplitude:", font_size=16, size_hint=(1, None),
                                    height=dp(32), color=(0.2, 0.2, 0.3, 1)))
        gridLayout.add_widget(self.amplitude_input)
        gridLayout.add_widget(Label(text="Frequency:", font_size=16, size_hint=(1, None),
                                    height=dp(32), color=(0.2, 0.2, 0.3, 1)))
        gridLayout.add_widget(self.frequency_input)
        gridLayout.add_widget(Label(text="Phase:", font_size=16, size_hint=(1, None),
                                    height=dp(32), color=(0.2, 0.2, 0.3, 1)))
        gridLayout.add_widget(self.phase_input)
        # Add button with margin
        button_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None), height=dp(50))
        button_anchor.add_widget(self.button)
        input_card.add_widget(gridLayout)
        input_card.add_widget(Widget(size_hint_y=None, height=dp(8)))
        input_card.add_widget(button_anchor)
        mainLayout.add_widget(input_card)
        return mainLayout
