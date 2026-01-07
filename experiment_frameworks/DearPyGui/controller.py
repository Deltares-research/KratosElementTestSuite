class Controller:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        # Build the UI and bind callbacks
        self.view.build(on_generate_callback=self.on_generate_graph)

    def start(self):
        self.update_fields_based_on_model()
        self.generate_and_display()  # optional initial plot
        self.view.run()

    def update_fields_based_on_model(self):
        self.view.set_fields(self.model.amplitude, self.model.frequency, self.model.phase)

    def update_model_based_on_inputs(self):
        try:
            amplitude, frequency, phase = self.view.get_fields()
            self.model.set_amplitude(amplitude)
            self.model.set_frequency(frequency)
            self.model.set_phase(phase)
        except (TypeError, ValueError) as exc:
            raise ValueError("Amplitude, frequency, and phase must be valid numbers.") from exc

    def generate_and_display(self):
        x_values, y_values = self.model.generate_graph_data()
        self.view.display_data(x_values, y_values)

    # Dear PyGui callback signature: (sender, app_data, user_data)
    def on_generate_graph(self, _sender, _app_data, _user_data=None):
        try:
            self.update_model_based_on_inputs()
            self.update_fields_based_on_model()
            self.generate_and_display()
        except ValueError as exc:
            self.view.show_error(str(exc))
