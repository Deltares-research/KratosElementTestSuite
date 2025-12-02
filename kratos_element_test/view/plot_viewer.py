import math
from tkinter import ttk

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec


class PlotViewer(ttk.Frame):
    def __init__(self, root, padding, width, height):
        super().__init__(root, padding=padding, width=width, height=height)
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
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

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
        self.canvas.draw()
