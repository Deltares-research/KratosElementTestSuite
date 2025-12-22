import sys
from PySide6.QtWidgets import QApplication

from model import Model
from controller import Controller
from view import SineWaveView

if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = Model()
    controller = Controller(model)
    window = SineWaveView(controller)
    window.resize(900, 650)
    window.show()

    sys.exit(app.exec())
