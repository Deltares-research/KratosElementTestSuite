import os
import dearpygui.dearpygui as dpg


class MyView:
    def __init__(self):
        # Widget tags (stable IDs)
        self.amplitude_tag = "amplitude_input"
        self.frequency_tag = "frequency_input"
        self.phase_tag = "phase_input"
        self.button_tag = "generate_button"
        self.series_tag = "sine_series"

        self.error_modal_tag = "error_modal"
        self.error_text_tag = "error_text"

        # Styling tags
        self.font_tag = "app_font"
        self.theme_tag = "app_theme"
        self.root_window_tag = "root_window"

    def build(self, on_generate_callback):
        dpg.create_context()

        self._configure_font()
        self._configure_theme()

        with dpg.window(
            label="Dear PyGui Sine Wave Example",
            tag=self.root_window_tag,
            width=900,
            height=650,
            no_collapse=True,
        ):
            # Header
            dpg.add_text("Sine Wave Demo")
            dpg.add_spacer(height=6)
            dpg.add_separator()
            dpg.add_spacer(height=10)

            # Plot "card"
            with dpg.child_window(height=390, border=True):
                dpg.add_text("Plot")
                dpg.add_spacer(height=6)

                with dpg.plot(label="", height=-1, width=-1):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="x")
                    y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="sin(x)")

                    dpg.add_line_series([], [], label="sin(x)", parent=y_axis, tag=self.series_tag)

            dpg.add_spacer(height=12)

            # Parameters "card"
            with dpg.child_window(height=-1, border=True):
                dpg.add_text("Parameters")
                dpg.add_spacer(height=10)

                label_w = 110
                input_w = 240

                with dpg.group(horizontal=True):
                    dpg.add_text("Amplitude")
                    dpg.add_spacer(width=max(0, label_w - 70))
                    dpg.add_input_float(tag=self.amplitude_tag, width=input_w, step=0.1, format="%.6g")

                with dpg.group(horizontal=True):
                    dpg.add_text("Frequency")
                    dpg.add_spacer(width=max(0, label_w - 72))
                    dpg.add_input_float(tag=self.frequency_tag, width=input_w, step=0.1, format="%.6g")

                with dpg.group(horizontal=True):
                    dpg.add_text("Phase")
                    dpg.add_spacer(width=max(0, label_w - 45))
                    dpg.add_input_float(tag=self.phase_tag, width=input_w, step=0.1, format="%.6g")

                dpg.add_spacer(height=12)
                dpg.add_separator()
                dpg.add_spacer(height=12)

                dpg.add_button(
                    label="Generate Graph",
                    tag=self.button_tag,
                    callback=on_generate_callback,
                    width=200,
                    height=36,
                )

        # Modal for input errors
        with dpg.window(
            label="Invalid input",
            modal=True,
            show=False,
            no_resize=True,
            no_move=True,
            no_collapse=True,
            tag=self.error_modal_tag,
            width=420,
            height=160,
        ):
            dpg.add_text("", tag=self.error_text_tag, wrap=390)
            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=10)
            dpg.add_button(
                label="OK",
                width=90,
                height=32,
                callback=lambda: dpg.configure_item(self.error_modal_tag, show=False),
            )

        dpg.create_viewport(title="Dear PyGui Sine Wave Example", width=900, height=650)
        dpg.setup_dearpygui()

        # Apply global styling
        if dpg.does_item_exist(self.font_tag):
            dpg.bind_font(self.font_tag)
        if dpg.does_item_exist(self.theme_tag):
            dpg.bind_theme(self.theme_tag)

    def _configure_font(self) -> None:
        candidates = [
            r"C:\Windows\Fonts\segoeui.ttf",   # Segoe UI
            r"C:\Windows\Fonts\seguisb.ttf",   # Segoe UI Semibold
            r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
        ]
        font_path = next((p for p in candidates if os.path.exists(p)), None)
        if not font_path:
            return

        with dpg.font_registry():
            dpg.add_font(font_path, 18, tag=self.font_tag)

    def _configure_theme(self) -> None:
        with dpg.theme(tag=self.theme_tag):
            # General styling
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 10)

                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 16, 14)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 8)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 10)
                dpg.add_theme_style(dpg.mvStyleVar_IndentSpacing, 14)

                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (18, 18, 20, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (24, 24, 28, 255))
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (28, 28, 33, 255))

                dpg.add_theme_color(dpg.mvThemeCol_Text, (235, 235, 240, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (150, 150, 160, 255))

                dpg.add_theme_color(dpg.mvThemeCol_Border, (55, 55, 65, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Separator, (55, 55, 65, 255))

                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (35, 35, 42, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (45, 45, 55, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (55, 55, 70, 255))

                dpg.add_theme_color(dpg.mvThemeCol_Button, (52, 88, 140, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (62, 102, 160, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (72, 115, 180, 255))

            # Plot styling (version-safe)
            # Some DPG versions use mvPlotCol_* enums; older/newer builds may differ.
            plot_bg = getattr(dpg, "mvPlotCol_PlotBg", None)
            plot_border = getattr(dpg, "mvPlotCol_PlotBorder", None)
            plot_grid = getattr(dpg, "mvPlotCol_GridLine", None)

            if plot_bg or plot_border or plot_grid:
                with dpg.theme_component(dpg.mvPlot):
                    if plot_bg:
                        dpg.add_theme_color(plot_bg, (24, 24, 28, 255))
                    if plot_border:
                        dpg.add_theme_color(plot_border, (55, 55, 65, 255))
                    if plot_grid:
                        dpg.add_theme_color(plot_grid, (55, 55, 65, 120))

    def run(self):
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    # --- MVC-facing methods ---
    def set_fields(self, amplitude: float, frequency: float, phase: float) -> None:
        dpg.set_value(self.amplitude_tag, float(amplitude))
        dpg.set_value(self.frequency_tag, float(frequency))
        dpg.set_value(self.phase_tag, float(phase))

    def get_fields(self) -> tuple[float, float, float]:
        # IMPORTANT: phase must come from self.phase_tag
        return (
            float(dpg.get_value(self.amplitude_tag)),
            float(dpg.get_value(self.frequency_tag)),
            float(dpg.get_value(self.phase_tag)),
        )

    def display_data(self, x_values, y_values) -> None:
        dpg.set_value(self.series_tag, [x_values, y_values])

    def show_error(self, message: str, title: str = "Invalid input") -> None:
        dpg.configure_item(self.error_modal_tag, label=title)
        dpg.set_value(self.error_text_tag, message)
        dpg.configure_item(self.error_modal_tag, show=True)
