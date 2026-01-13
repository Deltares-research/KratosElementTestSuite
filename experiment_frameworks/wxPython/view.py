import wx

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


class MyView(wx.Frame):
    def __init__(self, parent=None, title="wxPython Sine Wave Example"):
        super().__init__(parent, title=title, size=(900, 650))

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(250, 250, 255))

        # --- Inputs ---
        self.amplitude_input = wx.TextCtrl(panel, value="", style=wx.TE_PROCESS_ENTER)
        self.frequency_input = wx.TextCtrl(panel, value="", style=wx.TE_PROCESS_ENTER)
        self.phase_input = wx.TextCtrl(panel, value="", style=wx.TE_PROCESS_ENTER)

        self.button = wx.Button(panel, label="Generate Graph")

        input_grid = wx.FlexGridSizer(rows=3, cols=2, hgap=10, vgap=10)
        input_grid.AddGrowableCol(1, 1)

        label_style = wx.ALIGN_CENTER_VERTICAL

        input_grid.Add(wx.StaticText(panel, label="Amplitude:"), 0, label_style)
        input_grid.Add(self.amplitude_input, 1, wx.EXPAND)

        input_grid.Add(wx.StaticText(panel, label="Frequency:"), 0, label_style)
        input_grid.Add(self.frequency_input, 1, wx.EXPAND)

        input_grid.Add(wx.StaticText(panel, label="Phase:"), 0, label_style)
        input_grid.Add(self.phase_input, 1, wx.EXPAND)

        # --- Matplotlib figure/canvas ---
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("sin(x)")
        self.canvas = FigureCanvas(panel, -1, self.fig)

        # --- Layout ---
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Plot takes ~60% vertical space
        main_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 16)

        # Inputs card area
        inputs_box = wx.StaticBox(panel, label="Parameters")
        inputs_sizer = wx.StaticBoxSizer(inputs_box, wx.VERTICAL)
        inputs_sizer.Add(input_grid, 0, wx.EXPAND | wx.ALL, 12)

        button_row = wx.BoxSizer(wx.HORIZONTAL)
        button_row.AddStretchSpacer(1)
        button_row.Add(self.button, 0, wx.ALL, 0)
        button_row.AddStretchSpacer(1)

        inputs_sizer.Add(button_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        main_sizer.Add(inputs_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 16)

        panel.SetSizer(main_sizer)
        self.Centre()

    def set_fields(self, amplitude: float, frequency: float, phase: float) -> None:
        self.amplitude_input.SetValue(str(amplitude))
        self.frequency_input.SetValue(str(frequency))
        self.phase_input.SetValue(str(phase))

    def get_fields(self) -> tuple[str, str, str]:
        return (
            self.amplitude_input.GetValue(),
            self.frequency_input.GetValue(),
            self.phase_input.GetValue(),
        )

    def display_data(self, x_values, y_values) -> None:
        self.ax.clear()
        self.ax.plot(x_values, y_values, label="sin(x)", linewidth=2)
        self.ax.set_title("Example Sine Wave")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("sin(x)")
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()

    def show_error(self, message: str, title: str = "Invalid input") -> None:
        wx.MessageBox(message, title, style=wx.OK | wx.ICON_ERROR)
