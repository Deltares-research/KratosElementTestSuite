class Controller:
    def __init__(self, model):
        self.model = model

    def update_model(self, amplitude, frequency, phase):
        self.model.set_amplitude(amplitude)
        self.model.set_frequency(frequency)
        self.model.set_phase(phase)

    def generate_graph(self):
        return self.model.generate_graph_data()
