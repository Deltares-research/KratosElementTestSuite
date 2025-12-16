class Controller:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        view.button.bind(on_press=self.on_generate_graph)


    def start(self):
        self.view.run()

    def on_generate_graph(self, instance):
        amplitude = self.view.amplitude_input.text
        self.model.set_amplitude(amplitude)

        frequency = self.view.frequency_input.text
        self.model.set_frequency(frequency)

        phase = self.view.phase_input.text
        self.model.set_phase(phase)

        x_values, y_values = self.model.generate_graph_data()
        self.view.display_data(x_values, y_values)
