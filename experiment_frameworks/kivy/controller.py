class Controller:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        view.button.bind(on_press=self.on_generate_graph)


    def start(self):
        self.view.run()

    def on_generate_graph(self, instance):
        amplitude = self.view.amplitude_input.text
        print("Amplitude from view:", amplitude)
        self.model.set_amplitude(amplitude)

        frequency = self.view.frequency_input.text
        print("Frequency from view:", frequency)
        self.model.set_frequency(frequency)

        phase = self.view.phase_input.text
        print("Phase from view:", phase)
        self.model.set_phase(phase)

        self.model.generate_graph_data()
        self.view.plot_view.source = "graph.png"
        self.view.plot_view.reload()
