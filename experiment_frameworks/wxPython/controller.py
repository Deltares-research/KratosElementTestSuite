import wx


class Controller:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        # Button click
        self.view.button.Bind(wx.EVT_BUTTON, self.on_generate_graph)

        # Optional: hitting Enter in any field triggers graph generation
        self.view.amplitude_input.Bind(wx.EVT_TEXT_ENTER, self.on_generate_graph)
        self.view.frequency_input.Bind(wx.EVT_TEXT_ENTER, self.on_generate_graph)
        self.view.phase_input.Bind(wx.EVT_TEXT_ENTER, self.on_generate_graph)

    def start(self):
        self.update_fields_based_on_model()
        self.view.Show(True)

        # Initial plot (optional; comment out if you want blank at start)
        self.generate_and_display()

    def update_fields_based_on_model(self):
        self.view.set_fields(self.model.amplitude, self.model.frequency, self.model.phase)

    def update_model_based_on_inputs(self):
        amp, freq, phase = self.view.get_fields()

        try:
            self.model.set_amplitude(amp)
            self.model.set_frequency(freq)
            self.model.set_phase(phase)
        except (TypeError, ValueError) as exc:
            raise ValueError("Amplitude, frequency, and phase must be valid numbers.") from exc

    def generate_and_display(self):
        x_values, y_values = self.model.generate_graph_data()
        self.view.display_data(x_values, y_values)

    def on_generate_graph(self, event):
        try:
            self.update_model_based_on_inputs()
            self.update_fields_based_on_model()
            self.generate_and_display()
        except ValueError as exc:
            self.view.show_error(str(exc))
