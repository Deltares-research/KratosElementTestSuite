class Model:
    def __init__(self):
        self.amplitude = 1.0
        self.frequency = 1.0
        self.phase = 0.0

    def set_amplitude(self, amplitude):
        print("Setting amplitude in model to:", amplitude)
        self.amplitude = amplitude

    def set_frequency(self, frequency):
        print("Setting frequency in model to:", frequency)
        self.frequency = frequency

    def set_phase(self, phase):
        print("Setting phase in model to:", phase)
        self.phase = phase

    def generate_graph_data(self, x_values):
        import math

        y_values = [
            self.amplitude * math.sin(self.frequency * x + self.phase) for x in x_values
        ]
        return y_values
