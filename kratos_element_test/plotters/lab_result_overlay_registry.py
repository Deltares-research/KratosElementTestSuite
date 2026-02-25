import numpy as np
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple
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
)

Transform = Callable[[List[float]], List[float]]


@dataclass(frozen=True)
class OverlaySpec:
    axis_index: int
    x_key: Optional[str] = None
    y_key: Optional[str] = None
    label: str = "Experimental"
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    x_transform: Optional[Transform] = None
    y_transform: Optional[Transform] = None


def _abs_list(v: List[float]) -> List[float]:
    return list(np.abs(np.asarray(v, dtype=float)))


def _gamma_from_shear_strain_xy(v: List[float]) -> List[float]:
    # matches your direct shear plot: gamma_xy = 2 * shear_strain_xy, abs
    return list(np.abs(2.0 * np.asarray(v, dtype=float)))


OVERLAYS_BY_TEST: Dict[str, Tuple[OverlaySpec, ...]] = {
    "triaxial": (
        # axis 2: sigma1 vs sigma3 (x = sigma3, y = sigma1)
        OverlaySpec(
            axis_index=2,
            x_key="sigma_3",
            y_key="sigma_1",
            title=TITLE_SIGMA1_VS_SIGMA3,
            x_label=SIGMA3_LABEL,
            y_label=SIGMA1_LABEL,
        ),
        # axis 3: p vs q
        OverlaySpec(
            axis_index=3,
            x_key="p",
            y_key="q",
            title=TITLE_P_VS_Q,
            x_label=P_STRESS_LABEL,
            y_label=Q_STRESS_LABEL,
        )
    ),
    }