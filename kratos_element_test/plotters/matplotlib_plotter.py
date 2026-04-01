# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import numpy as np
from typing import Dict, List, Optional, Tuple
from kratos_element_test.model.core_utils import _fallback_log
from kratos_element_test.plotters.plotter_labels import (
    SIGMA1_LABEL,
    SIGMA3_LABEL,
    SIGMA1_SIGMA3_DIFF_LABEL,
    HORIZONTAL_STRESS_LABEL,
    VERTICAL_STRESS_LABEL,
    VERTICAL_STRAIN_LABEL,
    VOLUMETRIC_STRAIN_LABEL,
    SHEAR_STRAIN_LABEL,
    SHEAR_STRESS_LABEL,
    EFFECTIVE_STRESS_LABEL,
    MOBILIZED_SHEAR_STRESS_LABEL,
    P_STRESS_LABEL,
    Q_STRESS_LABEL,
    TIME_HOURS_LABEL,
    TITLE_SIGMA1_VS_SIGMA3,
    TITLE_DIFF_PRINCIPAL_SIGMA_VS_STRAIN,
    TITLE_VOL_VS_VERT_STRAIN,
    TITLE_MOHR,
    TITLE_P_VS_Q,
    TITLE_SHEAR_VS_STRAIN,
    TITLE_VERTICAL_STRAIN_VS_TIME,
    TITLE_VERTICAL_STRESS_VS_VERTICAL_STRAIN,
    TITLE_VERTICAL_STRESS_VS_HORIZONTAL_STRESS,
    LEGEND_MC,
    LEGEND_MC_FAILURE,
)
from kratos_element_test.plotters.lab_result_overlay_registry import OVERLAYS_BY_TEST

_PREFERRED_GENERIC_PAIRS_BY_TEST: Dict[str, Tuple[Tuple[str, str], ...]] = {
    "triaxial": (
        ("yy_strain", "sigma1_sigma3_diff"),
        ("yy_strain", "q"),
        ("sigma_3", "sigma_1"),
        ("p'", "q"),
    ),
    "direct_shear": (
        ("shear_strain_xy", "shear_stress_xy"),
        ("sigma_3", "sigma_1"),
        ("p'", "q"),
        ("yy_strain", "sigma1_sigma3_diff"),
    ),
    "crs": (
        ("yy_strain", "sigma_yy"),
        ("sigma_xx", "sigma_yy"),
        ("p'", "q"),
        ("time_steps", "yy_strain"),
    ),
}


class MatplotlibPlotter:
    def __init__(self, axes, logger=None):
        self._log = logger or _fallback_log
        self.axes = list(axes or [])

    def _clear(self):
        for ax in self.axes:
            try:
                ax.clear()
            except Exception:
                pass

    def _safe_legend(self, ax) -> None:
        handles, labels = ax.get_legend_handles_labels()
        if handles and labels:
            ax.legend()

    def _first_generic_axis_index(self, test_type: str) -> int:
        specs = OVERLAYS_BY_TEST.get(test_type, ())
        return specs[0].axis_index if specs else 0

    def _key_kind(self, key: str) -> str:
        normalized_key = (key or "").lower()
        if "time" in normalized_key:
            return "time"
        if "strain" in normalized_key or normalized_key in {"yy_strain", "vol_strain"}:
            return "strain"
        if (
            "sigma" in normalized_key
            or "stress" in normalized_key
            or normalized_key in {"p'", "q", "sigma1_sigma3_diff", "tau_xy"}
        ):
            return "stress"
        return "other"

    def _key_similarity(self, left: str, right: str) -> int:
        left_key = (left or "").lower()
        right_key = (right or "").lower()

        if left_key == right_key:
            return 8

        score = 0
        left_kind = self._key_kind(left_key)
        right_kind = self._key_kind(right_key)
        if left_kind == right_kind and left_kind != "other":
            score += 3

        if left_key in {"p'", "q"} and right_key in {"p'", "q"}:
            score += 4

        if "sigma" in left_key and "sigma" in right_key:
            score += 2
        if "strain" in left_key and "strain" in right_key:
            score += 2
        if "time" in left_key and "time" in right_key:
            score += 2

        return score

    def _axis_index_for_overlay_pair(
        self, test_type: str, x_key: str, y_key: str
    ) -> int:
        pair_specs = [
            spec
            for spec in OVERLAYS_BY_TEST.get(test_type, ())
            if spec.compute_xy is None
        ]

        for spec in pair_specs:
            x_candidate = spec.x_key
            y_candidate = spec.y_key
            if not x_candidate or not y_candidate:
                continue

            if x_candidate == x_key and y_candidate == y_key:
                return spec.axis_index

        for spec in pair_specs:
            x_candidate = spec.x_key
            y_candidate = spec.y_key
            if not x_candidate or not y_candidate:
                continue

            if x_candidate == y_key and y_candidate == x_key:
                return spec.axis_index

        best_axis = None
        best_score = -1
        for spec in pair_specs:
            x_candidate = spec.x_key
            y_candidate = spec.y_key
            if not x_candidate or not y_candidate:
                continue

            direct_score = self._key_similarity(
                x_key, x_candidate
            ) + self._key_similarity(y_key, y_candidate)
            reverse_score = self._key_similarity(
                x_key, y_candidate
            ) + self._key_similarity(y_key, x_candidate)
            score = max(direct_score, reverse_score)

            if score > best_score:
                best_score = score
                best_axis = spec.axis_index

        if best_axis is not None and best_score > 0:
            return best_axis

        return self._first_generic_axis_index(test_type)

    def _find_generic_overlay_pair(
        self, test_type: str, experimental_results: Dict[str, List[float]]
    ) -> Optional[Tuple[str, List[float], str, List[float]]]:
        def _trim_pair(
            x_key: str,
            x_values: List[float],
            y_key: str,
            y_values: List[float],
        ) -> Optional[Tuple[str, List[float], str, List[float]]]:
            n = min(len(x_values), len(y_values))
            if n <= 0:
                return None
            return x_key, list(x_values)[:n], y_key, list(y_values)[:n]

        for x_key, y_key in _PREFERRED_GENERIC_PAIRS_BY_TEST.get(test_type, ()):
            x_values = experimental_results.get(x_key)
            y_values = experimental_results.get(y_key)
            if x_values is None or y_values is None:
                continue
            pair = _trim_pair(x_key, x_values, y_key, y_values)
            if pair is not None:
                return pair

        series_items: List[Tuple[str, List[float]]] = []
        for key, values in experimental_results.items():
            if not isinstance(values, (list, tuple, np.ndarray)):
                continue
            if len(values) <= 0:
                continue
            series_items.append((key, list(values)))

        if len(series_items) < 2:
            return None

        x_key, x_values = series_items[0]
        y_key, y_values = series_items[1]
        return _trim_pair(x_key, x_values, y_key, y_values)

    def _apply_generic_experimental_overlay(
        self, test_type: str, experimental_results: Dict[str, List[float]]
    ) -> bool:
        out = self._find_generic_overlay_pair(test_type, experimental_results)
        if out is None:
            return False

        x_key, x, y_key, y = out
        axis_index = self._axis_index_for_overlay_pair(test_type, x_key, y_key)
        if axis_index >= len(self.axes):
            return False

        ax = self.axes[axis_index]
        ax.plot(x, y, "--", color="magenta", label=f"Lab results ({y_key} vs {x_key})")
        self._safe_legend(ax)

        if not ax.get_xlabel():
            ax.set_xlabel(x_key)
        if not ax.get_ylabel():
            ax.set_ylabel(y_key)

        self._log(
            f"Applied generic experimental overlay using '{x_key}' vs '{y_key}'.",
            "info",
        )
        return True

    def _apply_experimental_overlays(self, test_type: str, experimental_results) -> int:
        specs = OVERLAYS_BY_TEST.get(test_type, ())
        plotted_count = 0
        for spec in specs:
            if spec.axis_index >= len(self.axes):
                continue

            if spec.compute_xy is not None:
                out = spec.compute_xy(experimental_results)
                if out is None:
                    continue
                x, y = out
                n = min(len(x), len(y))
                if n <= 0:
                    continue
                self.axes[spec.axis_index].plot(
                    x[:n], y[:n], "--", color="magenta", label=spec.label
                )
                self._safe_legend(self.axes[spec.axis_index])
                plotted_count += 1
                continue

            if not spec.x_key or not spec.y_key:
                continue
            x = experimental_results.get(spec.x_key)
            y = experimental_results.get(spec.y_key)
            if x is None or y is None:
                continue

            if spec.x_transform is not None:
                x = spec.x_transform(x)
            if spec.y_transform is not None:
                y = spec.y_transform(y)

            n = min(len(x), len(y))
            if n <= 0:
                continue

            self.axes[spec.axis_index].plot(
                x[:n], y[:n], "--", color="magenta", label=spec.label
            )
            self._safe_legend(self.axes[spec.axis_index])
            plotted_count += 1

        return plotted_count

    def plot_experimental_only(
        self, test_type: str, experimental_results: Dict[str, List[float]]
    ) -> None:
        self._clear()

        specs = OVERLAYS_BY_TEST.get(test_type, ())
        if not specs or not experimental_results:
            return

        for spec in specs:
            if spec.axis_index >= len(self.axes):
                continue

            ax = self.axes[spec.axis_index]
            if spec.title:
                ax.set_title(spec.title)
            if spec.x_label:
                ax.set_xlabel(spec.x_label)
            if spec.y_label:
                ax.set_ylabel(spec.y_label)

            ax.grid(True)
            ax.locator_params(nbins=8)
            ax.minorticks_on()

            if spec.invert_x:
                ax.invert_xaxis()
            if spec.invert_y:
                ax.invert_yaxis()

        plotted_count = self._apply_experimental_overlays(
            test_type, experimental_results
        )
        if plotted_count == 0:
            self._apply_generic_experimental_overlay(test_type, experimental_results)

        for spec in specs:
            if spec.axis_index >= len(self.axes):
                continue
            ax = self.axes[spec.axis_index]
            ax.relim()
            ax.autoscale_view()

    def triaxial(
        self,
        yy,
        vol,
        sigma1,
        sigma3,
        p_list,
        q_list,
        cohesion=None,
        phi=None,
        experimental_results: Optional[Dict[str, List[float]]] = None,
    ):
        self._clear()
        # 0: |σ1-σ3| vs εyy
        self.plot_delta_sigma_triaxial(
            self.axes[0], yy, np.abs(np.array(sigma1) - np.array(sigma3))
        )
        # 1: εv vs εyy
        self.plot_volumetric_vertical_strain_triaxial(self.axes[1], yy, vol)
        # 2: σ1 vs σ3
        self.plot_principal_stresses_triaxial(self.axes[2], sigma1, sigma3)
        # 3: p' vs q
        self.plot_p_q_triaxial(self.axes[3], p_list, q_list)
        # 4: Mohr's Circle
        self.plot_mohr_circle_triaxial(
            self.axes[4], sigma1[-1], sigma3[-1], cohesion, phi
        )

        if experimental_results:
            plotted_count = self._apply_experimental_overlays(
                "triaxial", experimental_results
            )
            if plotted_count == 0:
                self._apply_generic_experimental_overlay(
                    "triaxial", experimental_results
                )

    def direct_shear(
        self,
        gamma_xy,
        tau_xy,
        sigma1,
        sigma3,
        p_list,
        q_list,
        cohesion=None,
        phi=None,
        experimental_results: Optional[Dict[str, List[float]]] = None,
    ):
        self._clear()
        # 0: τ vs γ
        self.plot_strain_stress_direct_shear(self.axes[0], gamma_xy, tau_xy)
        # 1: σ1 vs σ3
        self.plot_principal_stresses_direct_shear(self.axes[1], sigma1, sigma3)
        # 2: p' vs q
        self.plot_p_q_direct_shear(self.axes[2], p_list, q_list)
        # 3: Mohr's Circle
        self.plot_mohr_circle_direct_shear(
            self.axes[3], sigma1[-1], sigma3[-1], cohesion, phi
        )

        if experimental_results:
            plotted_count = self._apply_experimental_overlays(
                "direct_shear", experimental_results
            )
            if plotted_count == 0:
                self._apply_generic_experimental_overlay(
                    "direct_shear", experimental_results
                )

    def crs(
        self,
        yy_strain,
        time_steps,
        sigma_yy,
        sigma_xx,
        p_list,
        q_list,
        sigma1,
        sigma3,
        cohesion=None,
        phi=None,
        experimental_results: Optional[Dict[str, List[float]]] = None,
    ):
        self._clear()
        # 0: σýy vs εyy
        self.plot_vertical_stress_vs_vertical_strain_crs(
            self.axes[0], yy_strain, sigma_yy
        )
        # 1: σ'yy vs σ'xx
        self.plot_vertical_stress_vs_horizontal_stress_crs(
            self.axes[1], sigma_xx, sigma_yy
        )
        # 2: p' vs q
        self.plot_p_q_crs(self.axes[2], p_list, q_list)
        # 3: Mohr's Circle
        self.plot_mohr_circle_crs(self.axes[3], sigma1[-1], sigma3[-1], cohesion, phi)
        # 4: εyy vs time
        self.plot_vertical_strain_vs_time_crs(self.axes[4], yy_strain, time_steps)

        if experimental_results:
            plotted_count = self._apply_experimental_overlays(
                "crs", experimental_results
            )
            if plotted_count == 0:
                self._apply_generic_experimental_overlay("crs", experimental_results)

    def plot_principal_stresses_triaxial(self, ax, sigma_1, sigma_3):
        ax.plot(sigma_3, sigma_1, "-", color="blue", label="Kratos Simulation")
        ax.set_title(TITLE_SIGMA1_VS_SIGMA3)
        ax.set_xlabel(SIGMA3_LABEL)
        ax.set_ylabel(SIGMA1_LABEL)
        ax.grid(True)
        ax.locator_params(nbins=8)

        min_val = 0
        max_val_x = max(sigma_3)
        max_val_y = min(sigma_1)
        padding_x = 0.1 * (max_val_x - min_val)
        padding_y = 0.1 * (max_val_y - min_val)
        ax.set_xlim(min_val, max_val_x + padding_x)
        ax.set_ylim(min_val, max_val_y + padding_y)
        ax.minorticks_on()

    def plot_delta_sigma_triaxial(self, ax, vertical_strain, sigma_diff):
        ax.plot(
            vertical_strain,
            sigma_diff,
            "-",
            color="blue",
            label="Kratos Simulation",
        )
        ax.set_title(TITLE_DIFF_PRINCIPAL_SIGMA_VS_STRAIN)
        ax.set_xlabel(VERTICAL_STRAIN_LABEL)
        ax.set_ylabel(SIGMA1_SIGMA3_DIFF_LABEL)
        ax.grid(True)
        ax.invert_xaxis()
        ax.locator_params(nbins=8)
        ax.minorticks_on()

    def plot_volumetric_vertical_strain_triaxial(
        self, ax, vertical_strain, volumetric_strain
    ):
        ax.plot(
            vertical_strain,
            volumetric_strain,
            "-",
            color="blue",
            label="Kratos Simulation",
        )
        ax.set_title(TITLE_VOL_VS_VERT_STRAIN)
        ax.set_xlabel(VERTICAL_STRAIN_LABEL)
        ax.set_ylabel(VOLUMETRIC_STRAIN_LABEL)
        ax.grid(True)
        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.locator_params(nbins=8)
        ax.minorticks_on()

    def plot_mohr_circle_triaxial(
        self, ax, sigma_1, sigma_3, cohesion=None, friction_angle=None
    ):
        if np.isclose(sigma_1, sigma_3):
            self._log("σ₁ is equal to σ₃. Mohr circle collapses to a point.", "warn")
        center = (sigma_1 + sigma_3) / 2
        radius = (sigma_1 - sigma_3) / 2
        theta = np.linspace(0, np.pi, 200)
        sigma = center + radius * np.cos(theta)
        tau = -radius * np.sin(theta)

        ax.plot(sigma, tau, label="Kratos Simulation", color="blue")

        if cohesion is not None and friction_angle is not None:
            phi_rad = np.radians(friction_angle)
            x_line = np.linspace(0, sigma_1, 200)
            y_line = x_line * np.tan(phi_rad) - cohesion
            ax.plot(x_line, -y_line, "r--", label=LEGEND_MC_FAILURE)
            ax.legend(loc="upper left")

        ax.set_title(TITLE_MOHR)
        ax.set_xlabel(EFFECTIVE_STRESS_LABEL)
        ax.set_ylabel(MOBILIZED_SHEAR_STRESS_LABEL)
        ax.grid(True)
        ax.invert_xaxis()
        ax.set_xlim(left=0, right=1.2 * np.max(sigma_1))
        ax.set_ylim(bottom=0, top=-0.6 * np.max(sigma_1))
        ax.minorticks_on()

    def plot_p_q_triaxial(self, ax, p_list, q_list):
        ax.plot(p_list, q_list, "-", color="blue", label="Kratos Simulation")
        ax.set_title(TITLE_P_VS_Q)
        ax.set_xlabel(P_STRESS_LABEL)
        ax.set_ylabel(Q_STRESS_LABEL)
        ax.grid(True)
        ax.invert_xaxis()
        ax.locator_params(nbins=8)
        ax.minorticks_on()

    def plot_principal_stresses_direct_shear(self, ax, sigma_1, sigma_3):
        ax.plot(sigma_3, sigma_1, "-", color="blue", label="Kratos Simulation")
        ax.set_title(TITLE_SIGMA1_VS_SIGMA3)
        ax.set_xlabel(SIGMA3_LABEL)
        ax.set_ylabel(SIGMA1_LABEL)
        ax.grid(True)
        ax.locator_params(nbins=8)

        min_x, max_x = min(sigma_3), max(sigma_3)
        min_y, max_y = min(sigma_1), max(sigma_1)
        x_padding = 0.1 * (max_x - min_x) if max_x > min_x else 1.0
        y_padding = 0.1 * (max_y - min_y) if max_y > min_y else 1.0
        ax.set_xlim(min_x - x_padding, max_x + x_padding)
        ax.set_ylim(min_y - y_padding, max_y + y_padding)

        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.minorticks_on()

    def plot_strain_stress_direct_shear(self, ax, shear_strain_xy, shear_stress_xy):
        gamma_xy = 2 * np.array(shear_strain_xy)
        ax.plot(
            np.abs(gamma_xy),
            np.abs(shear_stress_xy),
            "-",
            color="blue",
            label="Kratos Simulation",
        )
        ax.set_title(TITLE_SHEAR_VS_STRAIN)
        ax.set_xlabel(SHEAR_STRAIN_LABEL)
        ax.set_ylabel(SHEAR_STRESS_LABEL)
        ax.grid(True)
        ax.locator_params(nbins=8)
        ax.minorticks_on()

    def plot_mohr_circle_direct_shear(
        self, ax, sigma_1, sigma_3, cohesion=None, friction_angle=None
    ):
        if np.isclose(sigma_1, sigma_3):
            self._log("σ₁ is equal to σ₃. Mohr circle collapses to a point.", "warn")
        center = (sigma_1 + sigma_3) / 2
        radius = (sigma_1 - sigma_3) / 2
        theta = np.linspace(0, np.pi, 400)
        sigma = center + radius * np.cos(theta)
        tau = -radius * np.sin(theta)

        ax.plot(sigma, tau, label="Kratos Simulation", color="blue")

        if cohesion is not None and friction_angle is not None:
            phi_rad = np.radians(friction_angle)
            max_sigma = center + radius
            x_line = np.linspace(0, max_sigma * 1.5, 400)
            y_line = x_line * np.tan(phi_rad) - cohesion
            ax.plot(x_line, -y_line, "r--", label=LEGEND_MC_FAILURE)
            ax.legend(loc="upper left")

        ax.set_title(LEGEND_MC)
        ax.set_xlabel(EFFECTIVE_STRESS_LABEL)
        ax.set_ylabel(MOBILIZED_SHEAR_STRESS_LABEL)
        ax.grid(True)
        ax.invert_xaxis()

        epsilon = 0.1
        relative_diff = np.abs(sigma_1 - sigma_3) / max(np.abs(sigma_1), 1e-6)

        if relative_diff < epsilon:
            ax.set_xlim(center - (1.2 * radius), center + (1.2 * radius))
            ax.set_ylim(bottom=0, top=-0.9 * (np.max(sigma_1) - np.max(sigma_3)))

        else:
            if sigma_1 > 0 or sigma_3 > 0:
                ax.set_xlim(left=1.2 * np.max(sigma_3), right=1.2 * np.max(sigma_1))
                ax.set_ylim(bottom=0, top=-0.9 * (np.max(sigma_1) - np.max(sigma_3)))
            else:
                ax.set_xlim(left=0, right=1.2 * np.max(sigma_1))
                ax.set_ylim(bottom=0, top=-0.9 * np.max(sigma_1))

        ax.minorticks_on()

    def plot_p_q_direct_shear(self, ax, p_list, q_list):
        ax.plot(p_list, q_list, "-", color="blue", label="Kratos Simulation")
        ax.set_title(TITLE_P_VS_Q)
        ax.set_xlabel(P_STRESS_LABEL)
        ax.set_ylabel(Q_STRESS_LABEL)
        ax.grid(True)
        ax.invert_xaxis()
        ax.set_xlim(left=0, right=1.2 * np.max(p_list))
        ax.locator_params(nbins=8)
        ax.minorticks_on()

    def plot_vertical_stress_vs_vertical_strain_crs(self, ax, yy_strain, sigma_yy):
        yy_strain.insert(0, 0.0)
        sigma_yy.insert(0, 0.0)
        ax.plot(
            yy_strain,
            sigma_yy,
            "-",
            color="blue",
            label="Kratos Simulation",
        )
        ax.set_title(TITLE_VERTICAL_STRESS_VS_VERTICAL_STRAIN)
        ax.set_xlabel(VERTICAL_STRAIN_LABEL)
        ax.set_ylabel(VERTICAL_STRESS_LABEL)
        ax.grid(True)
        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.locator_params(nbins=8)
        ax.minorticks_on()

    def plot_vertical_stress_vs_horizontal_stress_crs(self, ax, sigma_xx, sigma_yy):
        sigma_xx.insert(0, 0.0)
        ax.plot(
            sigma_xx,
            sigma_yy,
            "-",
            color="blue",
            label="Kratos Simulation",
        )
        ax.set_title(TITLE_VERTICAL_STRESS_VS_HORIZONTAL_STRESS)
        ax.set_xlabel(HORIZONTAL_STRESS_LABEL)
        ax.set_ylabel(VERTICAL_STRESS_LABEL)
        ax.grid(True)
        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.locator_params(nbins=8)
        ax.minorticks_on()

    def plot_p_q_crs(self, ax, p_list, q_list):
        p_list.insert(0, 0.0)
        q_list.insert(0, 0.0)
        ax.plot(p_list, q_list, "-", color="blue", label="Kratos Simulation")
        ax.set_title(TITLE_P_VS_Q)
        ax.set_xlabel(P_STRESS_LABEL)
        ax.set_ylabel(Q_STRESS_LABEL)
        ax.grid(True)
        ax.invert_xaxis()
        ax.locator_params(nbins=8)
        ax.minorticks_on()

    def plot_mohr_circle_crs(
        self, ax, sigma_1, sigma_3, cohesion=None, friction_angle=None
    ):
        if np.isclose(sigma_1, sigma_3):
            self._log("σ₁ is equal to σ₃. Mohr circle collapses to a point.", "warn")
        center = (sigma_1 + sigma_3) / 2
        radius = (sigma_1 - sigma_3) / 2
        theta = np.linspace(0, np.pi, 400)
        sigma = center + radius * np.cos(theta)
        tau = -radius * np.sin(theta)

        ax.plot(sigma, tau, label="Kratos Simulation", color="blue")

        if cohesion is not None and friction_angle is not None:
            phi_rad = np.radians(friction_angle)
            max_sigma = center + radius
            x_line = np.linspace(0, max_sigma * 1.5, 400)
            y_line = x_line * np.tan(phi_rad) - cohesion
            ax.plot(x_line, -y_line, "r--", label=LEGEND_MC_FAILURE)
            ax.legend(loc="upper left")

        ax.set_title(LEGEND_MC)
        ax.set_xlabel(EFFECTIVE_STRESS_LABEL)
        ax.set_ylabel(MOBILIZED_SHEAR_STRESS_LABEL)
        ax.grid(True)
        ax.invert_xaxis()

        epsilon = 0.1
        relative_diff = np.abs(sigma_1 - sigma_3) / (max(np.abs(sigma_3), 1e-6))

        if relative_diff < epsilon:
            ax.set_xlim(center - (1.2 * radius), center + (1.2 * radius))
            ax.set_ylim(bottom=0, top=-0.8 * (np.max(sigma_1) - np.max(sigma_3)))

        else:
            if sigma_1 > 0 or sigma_3 > 0:
                ax.set_xlim(left=0, right=1.2 * max(sigma_1, sigma_3))
                ax.set_ylim(bottom=0, top=(np.max(sigma_3) - np.max(sigma_1)))
            elif sigma_1 < 0 and sigma_3 < 0:
                ax.set_xlim(left=0, right=1.2 * np.max(sigma_1))
                ax.set_ylim(
                    bottom=0, top=(np.max(np.abs(sigma_1)) - np.max(np.abs(sigma_3)))
                )
            else:
                ax.set_xlim(left=0, right=1.2 * np.max(sigma_1))
                ax.set_ylim(bottom=0, top=-(np.max(sigma_3) - np.max(sigma_1)))

        ax.minorticks_on()

    def plot_vertical_strain_vs_time_crs(self, ax, yy_strain, time_steps):
        time_steps.insert(0, 0.0)
        ax.plot(
            time_steps,
            yy_strain,
            "-",
            color="blue",
            label="Kratos Simulation",
        )
        ax.set_title(TITLE_VERTICAL_STRAIN_VS_TIME)
        ax.set_xlabel(TIME_HOURS_LABEL)
        ax.set_ylabel(VERTICAL_STRAIN_LABEL)
        ax.grid(True)
        ax.locator_params(nbins=8)
        ax.minorticks_on()
