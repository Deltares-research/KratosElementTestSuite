from matplotlib import pyplot as plt


class Model:
    def __init__(self):
        self.amplitude = 1.0
        self.frequency = 1.0
        self.phase = 0.0

    def set_amplitude(self, amplitude):
        print("Setting amplitude in model to:", amplitude)
        self.amplitude = float(amplitude)

    def set_frequency(self, frequency):
        print("Setting frequency in model to:", frequency)
        self.frequency = float(frequency)

    def set_phase(self, phase):
        print("Setting phase in model to:", phase)
        self.phase = float(phase)

    def generate_graph_data(self):
        import math
        x_values = [i * 0.1 for i in range(100)]

        y_values = [
            self.amplitude * math.sin(self.frequency * x + self.phase) for x in x_values
        ]
        plt.plot(x_values, y_values)
        plt.savefig("graph.png")
        plt.close()
