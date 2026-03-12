# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import numpy as np
from typing import List, Optional, Tuple, Union

NumberOrList = Union[int, float, List[float]]


def _fallback_log(msg: str, level: str = "info") -> None:
    """
    Fallback logging function that prints messages to the console.
    """
    print(f"{level.upper()}: {msg}")


def seconds_to_hours(seconds: float) -> float:
    return seconds / 3600.0


def seconds_list_to_hours_list(second_list: list[float]) -> list[float]:
    return [seconds_to_hours(second) for second in second_list]


def hours_to_seconds(hours: float) -> float:
    return hours * 3600.0


def abs_list(values: List[float]) -> List[float]:
    return list(np.abs(np.asarray(values, dtype=float)))


def gamma_from_shear_strain_xy(values: List[float]) -> List[float]:
    return list(np.abs(2.0 * np.asarray(values, dtype=float)))


def last_float(value: NumberOrList) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, list) and len(value) > 0:
        return float(value[-1])
    return None


def compute_mohr_circle_xy(
    sigma_1: NumberOrList,
    sigma_3: NumberOrList,
    n_points: int = 200,
) -> Optional[Tuple[List[float], List[float]]]:
    s1 = last_float(sigma_1)
    s3 = last_float(sigma_3)
    if s1 is None or s3 is None:
        return None

    center = (s1 + s3) / 2.0
    radius = (s1 - s3) / 2.0

    theta = np.linspace(0.0, np.pi, n_points)
    sigma = center + radius * np.cos(theta)
    tau = -radius * np.sin(theta)

    return sigma.tolist(), tau.tolist()
