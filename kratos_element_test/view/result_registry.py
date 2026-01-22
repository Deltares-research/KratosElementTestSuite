# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

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
