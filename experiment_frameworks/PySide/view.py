from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QApplication
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SineWaveView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Sine Wave Generator")

        # Inputs
        self.amplitude_input = QLineEdit()
        self.frequency_input = QLineEdit()
        self.phase_input = QLineEdit()

        # Button
        self.button = QPushButton("Generate Graph")
        self.button.clicked.connect(self.on_generate_clicked)

        # Matplotlib canvas
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)

        # Layouts
        root = QVBoxLayout()

        root.addWidget(self.canvas)

        form = QFormLayout()
        form.addRow("Amplitude:", self.amplitude_input)
        form.addRow("Frequency:", self.frequency_input)
        form.addRow("Phase:", self.phase_input)

        bottom = QHBoxLayout()
        bottom.addLayout(form)
        bottom.addWidget(self.button)

        root.addLayout(bottom)
        self.setLayout(root)

        # Initialize fields from model
        self.refresh_inputs_from_model()
        self.plot_current_model()

    def refresh_inputs_from_model(self):
        m = self.controller.model
        self.amplitude_input.setText(str(m.amplitude))
        self.frequency_input.setText(str(m.frequency))
        self.phase_input.setText(str(m.phase))

    def update_model_from_inputs(self):
        self.controller.update_model(
            self.amplitude_input.text(),
            self.frequency_input.text(),
            self.phase_input.text(),
        )

    def plot_current_model(self):
        x, y = self.controller.generate_graph()
        self.ax.clear()
        self.ax.plot(x, y, linewidth=2)
        self.ax.set_title("Example Sine Wave")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("sin(x)")
        self.ax.legend(["sin(x)"])
        self.canvas.draw()

    def on_generate_clicked(self):
        try:
            self.update_model_from_inputs()
            self.refresh_inputs_from_model()
            self.plot_current_model()
        except ValueError:
            # Minimal handling: ignore bad float input
            # You can replace this with a QMessageBox if you want.
            pass
