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

    def build(self, on_generate_callback):
        dpg.create_context()

        with dpg.window(label="Dear PyGui Sine Wave Example", width=900, height=650):
            # Plot area (top ~60%)
            with dpg.child_window(height=380, border=False):
                with dpg.plot(label="Plot", height=-1, width=-1):
                    dpg.add_plot_legend()

                    x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="x")
                    y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="sin(x)")

                    # Start with empty series; Controller will set initial values
                    dpg.add_line_series([], [], label="sin(x)", parent=y_axis, tag=self.series_tag)

            # Inputs area (bottom ~40%)
            with dpg.child_window(height=-1, border=True):
                dpg.add_text("Parameters")

                with dpg.group(horizontal=True):
                    dpg.add_text("Amplitude:", bullet=False)
                    dpg.add_input_float(tag=self.amplitude_tag, width=200, step=0.1, format="%.6g")

                with dpg.group(horizontal=True):
                    dpg.add_text("Frequency:", bullet=False)
                    dpg.add_input_float(tag=self.frequency_tag, width=200, step=0.1, format="%.6g")

                with dpg.group(horizontal=True):
                    dpg.add_text("Phase:", bullet=False)
                    dpg.add_input_float(tag=self.phase_tag, width=200, step=0.1, format="%.6g")

                dpg.add_spacer(height=8)

                dpg.add_button(
                    label="Generate Graph",
                    tag=self.button_tag,
                    callback=on_generate_callback,
                    width=200,
                )

        # Simple modal for input errors
        with dpg.window(
            label="Invalid input",
            modal=True,
            show=False,
            no_resize=True,
            no_move=True,
            no_collapse=True,
            tag=self.error_modal_tag,
            width=380,
            height=140,
        ):
            dpg.add_text("", tag=self.error_text_tag, wrap=360)
            dpg.add_spacer(height=8)
            dpg.add_button(label="OK", width=80, callback=lambda: dpg.configure_item(self.error_modal_tag, show=False))

        dpg.create_viewport(title="Dear PyGui Sine Wave Example", width=900, height=650)
        dpg.setup_dearpygui()

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
        return (
            float(dpg.get_value(self.amplitude_tag)),
            float(dpg.get_value(self.frequency_tag)),
            float(dpg.get_value(self.phase_tag)),
        )

    def display_data(self, x_values, y_values) -> None:
        # Dear PyGui line series expects value = [x_list, y_list]
        dpg.set_value(self.series_tag, [x_values, y_values])

    def show_error(self, message: str, title: str = "Invalid input") -> None:
        dpg.configure_item(self.error_modal_tag, label=title)
        dpg.set_value(self.error_text_tag, message)
        dpg.configure_item(self.error_modal_tag, show=True)
