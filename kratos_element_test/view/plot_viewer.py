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
        self._axes = []
        self._plotter = None
        self._canvas = None
        self._grid_spec = None
        self._figure = None

    def initialize(self, num_plots):
        self.clear()

        self._figure = plt.figure(figsize=(12, 8), dpi=100)
        rows = math.ceil(math.sqrt(num_plots))
        cols = math.ceil(num_plots / rows)

        self._grid_spec = GridSpec(
            rows, cols, figure=self._figure, wspace=0.4, hspace=0.6
        )
        self._axes = [
            self._figure.add_subplot(self._grid_spec[i]) for i in range(num_plots)
        ]
        self._plotter = MatplotlibPlotter(self._axes, logger=None)
        self._canvas = FigureCanvasTkAgg(self._figure, master=self)
        self._canvas.draw()
        toolbar = NavigationToolbar2Tk(self._canvas, self)
        toolbar.update()
        toolbar.pack(side="bottom", fill="x")
        self._canvas.get_tk_widget().pack(fill="both", expand=True)
        self.draw()

    def clear(self):
        if self.winfo_exists():
            for widget in self.winfo_children():
                widget.destroy()
        self._axes = []
        self._figure = None
        self._canvas = None

    def draw(self):
        results = self._result_controller.get_latest_results()
        if len(results) == 0:
            return

        test_type = TEST_NAME_TO_TYPE.get(self._result_controller.get_current_test())
        if test_type == "triaxial":
            self._plotter.triaxial(
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
            self._plotter.direct_shear(
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
            self._plotter.crs(
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
        self._canvas.draw()
