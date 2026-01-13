import math
from kivy.uix.boxlayout import BoxLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.gridspec import GridSpec
from kivy.graphics.texture import Texture
from kivy.uix.image import Image as KivyImage
from io import BytesIO

from kratos_element_test.plotters.matplotlib_plotter import MatplotlibPlotter
from kratos_element_test.view.ui_constants import TEST_NAME_TO_TYPE


class PlotViewer(BoxLayout):
    def __init__(self, result_controller, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        super().__init__(**kwargs)
        self._result_controller = result_controller
        self.axes = []
        self.canvas_widget = None
        self.gs = None
        self.fig = None
        
        # Configure matplotlib with a default theme
        self._configure_matplotlib_theme()

    def _configure_matplotlib_theme(self):
        """Configure matplotlib with default dark theme"""
        plt.rcParams.update({
            'figure.facecolor': '#1e1e1e',
            'axes.facecolor': '#1e1e1e',
            'axes.edgecolor': '#ffffff',
            'axes.labelcolor': '#ffffff',
            'text.color': '#ffffff',
            'xtick.color': '#ffffff',
            'ytick.color': '#ffffff',
            'grid.color': '#ffffff',
            'grid.alpha': 0.3,
            'legend.facecolor': '#1e1e1e',
            'legend.edgecolor': '#ffffff',
        })

    def initialize(self, num_plots):
        self.clear()

        self.fig = plt.figure(figsize=(12, 8), dpi=100)
        rows = math.ceil(math.sqrt(num_plots))
        cols = math.ceil(num_plots / rows)

        self.gs = GridSpec(rows, cols, figure=self.fig, wspace=0.4, hspace=0.6)
        self.axes = [self.fig.add_subplot(self.gs[i]) for i in range(num_plots)]
        
        # Create Kivy image widget to display matplotlib figure
        self.canvas_widget = KivyImage()
        self.add_widget(self.canvas_widget)
        self.draw()

    def clear(self):
        self.clear_widgets()
        self.axes = []
        if self.fig is not None:
            plt.close(self.fig)
        self.fig = None
        self.canvas_widget = None

    def get_canvas(self):
        return self.canvas_widget

    def get_axes(self):
        return self.axes

    def draw(self):
        plotter = MatplotlibPlotter(self.axes, logger=None, line_color='#3498db')
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
        
        # Convert matplotlib figure to Kivy texture
        self._update_canvas()

    def _update_canvas(self):
        """Convert matplotlib figure to Kivy texture"""
        if self.fig is None or self.canvas_widget is None:
            return
        
        # Render figure to buffer
        canvas = FigureCanvasAgg(self.fig)
        canvas.draw()
        
        # Get the RGBA buffer from the figure
        buf = canvas.buffer_rgba()
        w, h = canvas.get_width_height()
        
        # Create Kivy texture from buffer
        texture = Texture.create(size=(w, h), colorfmt='rgba')
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        
        # Update image widget
        self.canvas_widget.texture = texture
