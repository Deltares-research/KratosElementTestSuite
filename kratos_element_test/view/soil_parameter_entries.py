from kivy.uix.boxlayout import BoxLayout


class SoilParameterEntries(BoxLayout):
    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('spacing', 10)
        kwargs.setdefault('padding', 10)
        super().__init__(**kwargs)