import math
from tkinter import ttk

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.gridspec import GridSpec

from kratos_element_test.plotters.matplotlib_plotter import MatplotlibPlotter
from kratos_element_test.view.ui_constants import TEST_NAME_TO_TYPE


class PlotViewer(ttk.Frame):
    def __init__(self, result_controller, root, padding, width, height):
        super().__init__(root, padding=padding, width=width, height=height)
        self._result_controller = result_controller
        self.axes = []
        self.canvas = None
        self.gs = None
        self.fig = None

    def initialize(self, num_plots):
        self.clear()

        self.fig = plt.figure(figsize=(12, 8), dpi=100)
        rows = math.ceil(math.sqrt(num_plots))
        cols = math.ceil(num_plots / rows)

        self.gs = GridSpec(rows, cols, figure=self.fig, wspace=0.4, hspace=0.6)
        self.axes = [self.fig.add_subplot(self.gs[i]) for i in range(num_plots)]
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        toolbar.pack(side="bottom", fill="x")
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.draw()

    def clear(self):
        if self.winfo_exists():
            for widget in self.winfo_children():
                widget.destroy()
        self.axes = []
        self.fig = None
        self.canvas = None

    def get_canvas(self):
        return self.canvas

    def get_axes(self):
        return self.axes

    def draw(self):
        plotter = MatplotlibPlotter(self.axes, logger=None)
        results = self._result_controller.get_latest_results()
        if len(results) == 0:
            return
        test_type = TEST_NAME_TO_TYPE.get(self._result_controller.get_current_test())
        if test_type == "triaxial":
            plotter.triaxial(
                results["yy_strain"],
                results["vol_strain"],
                results["sigma1"],
                results["sigma3"],
                results["mean_stress"],
                results["von_mises"],
                results["cohesion"],
                results["phi"],
            )
        elif test_type == "direct_shear":
            plotter.direct_shear(
                results["shear_strain_xy"],
                results["shear_xy"],
                results["sigma1"],
                results["sigma3"],
                results["mean_stress"],
                results["von_mises"],
                results["cohesion"],
                results["phi"],
            )
        elif test_type == "crs":
            plotter.crs(
                results["yy_strain"],
                results["time_steps"],
                results["sigma_yy"],
                results["sigma_xx"],
                results["mean_stress"],
                results["von_mises"],
                results["sigma1"],
                results["sigma3"],
                results["cohesion"],
                results["phi"],
            )
        else:
            raise ValueError(f"Unsupported test_type: {test_type}")
        self.canvas.draw()
