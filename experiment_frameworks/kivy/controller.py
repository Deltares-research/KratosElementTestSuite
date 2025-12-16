class Controller:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        view.button.bind(on_press=self.on_generate_graph)

    def start(self):
        self.view.run()
        self.update_fields_based_on_model()

    def update_fields_based_on_model(self):
        self.view.amplitude_input.text = str(self.model.amplitude)
        self.view.frequency_input.text = str(self.model.frequency)
        self.view.phase_input.text = str(self.model.phase)

    def on_generate_graph(self, instance):
        self.update_model_based_on_inputs()
        self.update_fields_based_on_model()
        x_values, y_values = self.model.generate_graph_data()
        self.view.display_data(x_values, y_values)

    def update_model_based_on_inputs(self):
        amplitude = self.view.amplitude_input.text
        self.model.set_amplitude(amplitude)

        frequency = self.view.frequency_input.text
        self.model.set_frequency(frequency)

        phase = self.view.phase_input.text
        self.model.set_phase(phase)
