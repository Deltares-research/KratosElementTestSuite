# ©Deltares 2026
# This is a prototype version
# Contact kratos@deltares.nl

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple
from kratos_element_test.model.core_utils import (
    abs_list,
    gamma_from_shear_strain_xy,
    compute_mohr_circle_xy,
)
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
ComputeXY = Callable[
    [Dict[str, List[float]]], Optional[Tuple[List[float], List[float]]]
]


@dataclass(frozen=True)
class OverlaySpec:
    axis_index: int
    x_key: Optional[str] = None
    y_key: Optional[str] = None
    label: str = "Lab results"
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    x_transform: Optional[Transform] = None
    y_transform: Optional[Transform] = None
    compute_xy: Optional[ComputeXY] = None
    invert_x: bool = False
    invert_y: bool = False


def compute_mohr_circle_xy_from_results(
    exp: Dict[str, List[float]],
) -> Optional[Tuple[List[float], List[float]]]:
    return compute_mohr_circle_xy(exp.get("sigma_1"), exp.get("sigma_3"))


OVERLAYS_BY_TEST: Dict[str, Tuple[OverlaySpec, ...]] = {
    "triaxial": (
        # axis 0: |sigma1 - sigma3| vs yy_strain
        OverlaySpec(
            axis_index=0,
            x_key="yy_strain",
            y_key="sigma1_sigma3_diff",
            title=TITLE_DIFF_PRINCIPAL_SIGMA_VS_STRAIN,
            x_label=VERTICAL_STRAIN_LABEL,
            y_label=SIGMA1_SIGMA3_DIFF_LABEL,
            invert_x=True,
        ),
        # axis 1: vol_strain vs yy_strain
        OverlaySpec(
            axis_index=1,
            x_key="yy_strain",
            y_key="vol_strain",
            title=TITLE_VOL_VS_VERT_STRAIN,
            x_label=VERTICAL_STRAIN_LABEL,
            y_label=VOLUMETRIC_STRAIN_LABEL,
            invert_x=True,
            invert_y=True,
        ),
        # axis 2: sigma1 vs sigma3
        OverlaySpec(
            axis_index=2,
            x_key="sigma_3",
            y_key="sigma_1",
            title=TITLE_SIGMA1_VS_SIGMA3,
            x_label=SIGMA3_LABEL,
            y_label=SIGMA1_LABEL,
        ),
        # axis 3: p' vs q
        OverlaySpec(
            axis_index=3,
            x_key="p'",
            y_key="q",
            title=TITLE_P_VS_Q,
            x_label=P_STRESS_LABEL,
            y_label=Q_STRESS_LABEL,
            invert_x=True,
        ),
        # axis 4: Mohr's circle
        OverlaySpec(
            axis_index=4,
            label="Lab results",
            title=TITLE_MOHR,
            x_label=EFFECTIVE_STRESS_LABEL,
            y_label=MOBILIZED_SHEAR_STRESS_LABEL,
            compute_xy=compute_mohr_circle_xy_from_results,
            invert_x=True,
        ),
    ),
    "direct_shear": (
        # axis 0: tau vs gamma
        OverlaySpec(
            axis_index=0,
            x_key="shear_strain_xy",
            y_key="shear_stress_xy",
            title=TITLE_SHEAR_VS_STRAIN,
            x_label=SHEAR_STRAIN_LABEL,
            y_label=SHEAR_STRESS_LABEL,
            x_transform=gamma_from_shear_strain_xy,
            y_transform=abs_list,
        ),
        # axis 1: sigma1 vs sigma3
        OverlaySpec(
            axis_index=1,
            x_key="sigma_3",
            y_key="sigma_1",
            title=TITLE_SIGMA1_VS_SIGMA3,
            x_label=SIGMA3_LABEL,
            y_label=SIGMA1_LABEL,
            invert_x=True,
            invert_y=True,
        ),
        # axis 2: p' vs q
        OverlaySpec(
            axis_index=2,
            x_key="p'",
            y_key="q",
            title=TITLE_P_VS_Q,
            x_label=P_STRESS_LABEL,
            y_label=Q_STRESS_LABEL,
        ),
        # axis 3: Mohr's circle
        OverlaySpec(
            axis_index=3,
            label="Lab results",
            title=TITLE_MOHR,
            x_label=EFFECTIVE_STRESS_LABEL,
            y_label=MOBILIZED_SHEAR_STRESS_LABEL,
            compute_xy=compute_mohr_circle_xy_from_results,
            invert_x=True,
        ),
    ),
    "crs": (
        # axis 0: sigma_yy vs yy_strain
        OverlaySpec(
            axis_index=0,
            x_key="yy_strain",
            y_key="sigma_yy",
            title=TITLE_VERTICAL_STRESS_VS_VERTICAL_STRAIN,
            x_label=VERTICAL_STRAIN_LABEL,
            y_label=VERTICAL_STRESS_LABEL,
            invert_x=True,
            invert_y=True,
        ),
        # axis 1: sigma_yy vs sigma_xx
        OverlaySpec(
            axis_index=1,
            x_key="sigma_xx",
            y_key="sigma_yy",
            title=TITLE_VERTICAL_STRESS_VS_HORIZONTAL_STRESS,
            x_label=HORIZONTAL_STRESS_LABEL,
            y_label=VERTICAL_STRESS_LABEL,
            invert_x=True,
            invert_y=True,
        ),
        # axis 2: p' vs q
        OverlaySpec(
            axis_index=2,
            x_key="p'",
            y_key="q",
            title=TITLE_P_VS_Q,
            x_label=P_STRESS_LABEL,
            y_label=Q_STRESS_LABEL,
            invert_x=True,
        ),
        # axis 3: Mohr's circle
        OverlaySpec(
            axis_index=3,
            label="Lab results",
            title=TITLE_MOHR,
            x_label=EFFECTIVE_STRESS_LABEL,
            y_label=MOBILIZED_SHEAR_STRESS_LABEL,
            compute_xy=compute_mohr_circle_xy_from_results,
            invert_x=True,
        ),
        # axis 4: yy_strain vs time_steps
        OverlaySpec(
            axis_index=4,
            x_key="time_steps",
            y_key="yy_strain",
            title=TITLE_VERTICAL_STRAIN_VS_TIME,
            x_label=TIME_HOURS_LABEL,
            y_label=VERTICAL_STRAIN_LABEL,
        ),
    ),
}
