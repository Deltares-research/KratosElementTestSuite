from view import MyView
from controller import Controller
from model import Model

if __name__ == "__main__":
    controller = Controller(MyView(), Model())
    controller.start()
