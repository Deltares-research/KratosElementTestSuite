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
