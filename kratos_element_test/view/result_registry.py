# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

from tkinter import messagebox

_ui_instance = None

PLOT_MAPPING = {
    "triaxial": [
        ("delta_sigma", "yy_strain", "Δσ = |σ1-σ3| (kPa)", "Vertical Strain εyy"),
        ("vol_strain", "yy_strain", "Volumetric Strain εv", "Vertical Strain εyy"),
        ("sigma1", "sigma3", "σ1 (kPa)", "σ3 (kPa)"),
        ("von_mises", "mean_stress", "q (kPa)", "p′ (kPa)"),
        ("mohr_circle", None, "τ (kPa)", "σ′ (kPa)"),
    ],
    "direct_shear": [
        ("shear_xy_abs", "gamma_xy_abs", "Shear Stress τxy (kPa)", "Shear Strain γxy"),
        ("sigma1", "sigma3", "σ1 (kPa)", "σ3 (kPa)"),
        ("von_mises", "mean_stress", "q (kPa)", "p′ (kPa)"),
        ("mohr_circle", None, "τ (kPa)", "σ′ (kPa)"),
    ],
    "crs": [
        ("sigma_yy", "yy_strain", "σ′yy (kPa)", "Vertical Strain εyy"),
        ("sigma_yy", "sigma_xx", "σ′yy (kPa)", "σ′xx (kPa)"),
        ("von_mises", "mean_stress", "q (kPa)", "p′ (kPa)"),
        ("mohr_circle", None, "τ (kPa)", "σ′ (kPa)"),
        ("yy_strain", "time_steps", "Vertical Strain εyy", "Time (h)"),
    ],
}


def register_ui_instance(ui):
    global _ui_instance
    _ui_instance = ui


def get_latest_results():
    if _ui_instance and hasattr(_ui_instance, "latest_results"):
        return _ui_instance.latest_results
    else:
        messagebox.showerror("Export Error", "No results available to export yet.")
        return {}


def get_latest_test_type():
    if _ui_instance and hasattr(_ui_instance, "latest_test_type"):
        return _ui_instance.latest_test_type or ""
    messagebox.showerror("Export Error", "No test type available to export yet.")
    return ""
