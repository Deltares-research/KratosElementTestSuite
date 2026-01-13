import streamlit as st
import matplotlib.pyplot as plt

from model import Model


def _get_model() -> Model:
    if "model" not in st.session_state:
        st.session_state.model = Model()
    return st.session_state.model


def main():
    st.set_page_config(page_title="Sine Wave Generator", layout="centered")
    st.title("Sine Wave Generator")

    model = _get_model()

    st.subheader("Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        amplitude = st.number_input(
            "Amplitude",
            value=float(model.amplitude),
            step=0.1,
            format="%.6f",
        )

    with col2:
        frequency = st.number_input(
            "Frequency",
            value=float(model.frequency),
            step=0.1,
            format="%.6f",
        )

    with col3:
        phase = st.number_input(
            "Phase",
            value=float(model.phase),
            step=0.1,
            format="%.6f",
        )

    generate = st.button("Generate Graph", type="primary")

    model.set_amplitude(amplitude)
    model.set_frequency(frequency)
    model.set_phase(phase)

    if generate or st.session_state.get("has_plotted", False):
        st.session_state.has_plotted = True

        x_values, y_values = model.generate_graph_data()

        fig, ax = plt.subplots()
        ax.plot(x_values, y_values, linewidth=2)
        ax.set_title("Example Sine Wave")
        ax.set_xlabel("x")
        ax.set_ylabel("sin(x)")
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)

        st.pyplot(fig, clear_figure=True)

        with st.expander("Show generated data"):
            st.write(
                {
                    "x_values_sample": x_values[:10],
                    "y_values_sample": y_values[:10],
                    "count": len(x_values),
                }
            )


if __name__ == "__main__":
    main()
