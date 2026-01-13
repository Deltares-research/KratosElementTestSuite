import wx

from view import MyView
from controller import Controller
from model import Model


if __name__ == "__main__":
    app = wx.App(False)

    model = Model()
    view = MyView(title="wxPython Sine Wave Example")
    controller = Controller(view, model)
    controller.start()

    app.MainLoop()
