from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from KratosMultiphysics.GeoMechanicsApplication.gid_output_file_reader import (
    GiDOutputFileReader,
)

from kratos_element_test.model.core_utils import seconds_to_hours
from kratos_element_test.view.ui_logger import log_message as fallback_log


class ResultCollector:
    def __init__(
        self,
        output_file_paths,
        cohesion=None,
        phi=None,
        drainage_type="drained",
        logger=None,
    ):
        self.output_file_paths = output_file_paths
        self._log = logger or fallback_log
        self.cohesion = cohesion
        self.phi = phi
        self.drainage_type = drainage_type

    def collect_results(self):
        all_tensors = {}
        xx_strain_stages = []
        yy_strain_stages = []
        zz_strain_stages = []
        xy_strain_stages = []
        all_shear_stress_xy = []
        all_vol_strain = []
        all_shear_strain_xy = []
        all_von_mises = []
        all_mean_stress = []
        all_sigma_xx = []
        all_sigma_yy = []
        all_time_steps = []
        all_water_pressures = []

        for result_path in self.output_file_paths:
            s, ms, vm, d, e, wp, t = self._read_results(result_path)

            tensors = self._extract_stress_tensors(s)
            shear_stress_xy = self._extract_shear_stress_xy(s)
            yy_strain, vol_strain, shear_strain_xy = self._compute_strains(e)
            xx, yy, zz, xy, vol, shear_xy_strain = self._compute_strains(e)
            von_mises_values = self._compute_scalar_stresses(vm)
            mean_stress_values = self._compute_scalar_stresses(ms)
            sigma_xx, sigma_yy = self._extract_sigma_xx_yy(s)
            time_steps = t
            all_water_pressures.extend(self._extract_water_pressure(wp))

            for time, tensor_list in tensors.items():
                all_tensors.setdefault(time, []).extend(tensor_list)

            all_shear_stress_xy.extend(shear_stress_xy)
            xx_strain_stages.append(xx)
            yy_strain_stages.append(yy)
            zz_strain_stages.append(zz)
            xy_strain_stages.append(xy)
            all_vol_strain.extend(vol_strain)
            all_shear_strain_xy.extend(shear_strain_xy)
            all_von_mises.extend(von_mises_values)
            all_mean_stress.extend(mean_stress_values)
            all_sigma_xx.extend(sigma_xx)
            all_sigma_yy.extend(sigma_yy)
            all_time_steps.extend([seconds_to_hours(t) for t in time_steps])

        all_xx_strain = self._apply_cumulative_strain_offset(xx_strain_stages)
        all_yy_strain = self._apply_cumulative_strain_offset(yy_strain_stages)
        all_zz_strain = self._apply_cumulative_strain_offset(zz_strain_stages)
        all_xy_strain = self._apply_cumulative_strain_offset(xy_strain_stages)

        all_excess_pore_pressure = []
        if self.drainage_type == "undrained" and all_water_pressures:
            initial_pressure = all_water_pressures[0]
            all_excess_pore_pressure = [
                p - initial_pressure for p in all_water_pressures
            ]

        sigma_1, sigma_3 = self._calculate_principal_stresses(all_tensors)

        return {
            "yy_strain": all_yy_strain,
            "vol_strain": all_vol_strain,
            "epsilon_1": epsilon_1,
            "sigma1": sigma_1,
            "sigma3": sigma_3,
            "shear_xy": all_shear_stress_xy,
            "shear_strain_xy": all_shear_strain_xy,
            "mean_stress": all_mean_stress,
            "von_mises": all_von_mises,
            "cohesion": self.cohesion,
            "phi": self.phi,
            "sigma_xx": all_sigma_xx,
            "sigma_yy": all_sigma_yy,
            "time_steps": all_time_steps,
            "excess_pore_pressure": all_excess_pore_pressure,
        }

    def _calculate_excess_pore_pressure(self, result_paths: List[str]) -> List[float]:
        all_water_pressures = []
        for path in result_paths:
            _, _, _, _, _, wp, _ = self._read_results(path)
            water_pressure_values = self._extract_water_pressure(wp)
            all_water_pressures.extend(water_pressure_values)

        if not all_water_pressures:
            return []

        initial_pressure = all_water_pressures[0]
        return [p - initial_pressure for p in all_water_pressures]

    def _read_output(self, result_path: Path) -> dict:
        return GiDOutputFileReader().read_output_from(result_path)

    def _read_results(self, result_path: Path):
        result_path = Path(result_path)
        (
            stress,
            mean_stress,
            von_mises,
            displacement,
            strain,
            water_pressure,
            time_steps,
        ) = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )

        if not result_path.exists():
            self._log(f"Missing result file: {result_path}", "warn")
            return (
                stress,
                mean_stress,
                von_mises,
                displacement,
                strain,
                water_pressure,
                time_steps,
            )

        output = self._read_output(result_path)

        for result_name, items in output.get("results", {}).items():
            for item in items:
                self._categorize_result(
                    result_name,
                    item,
                    stress,
                    mean_stress,
                    von_mises,
                    displacement,
                    strain,
                    water_pressure=water_pressure,
                )

        time_steps = GiDOutputFileReader.get_time_steps_from_first_valid_result(output)

        return (
            stress,
            mean_stress,
            von_mises,
            displacement,
            strain,
            water_pressure,
            time_steps,
        )

    def _categorize_result(
        self,
        result_name,
        item,
        stress,
        mean_stress,
        von_mises,
        displacement,
        strain,
        water_pressure=None,
    ):
        if water_pressure is None:
            water_pressure = []

        values = item["values"]
        if result_name == "CAUCHY_STRESS_TENSOR":
            stress.append(item)
        elif result_name == "MEAN_EFFECTIVE_STRESS" and self._is_tri3_element_gp(
            values
        ):
            mean_stress.append(item)
        elif result_name == "VON_MISES_STRESS" and self._is_tri3_element_gp(values):
            von_mises.append(item)
        elif result_name == "DISPLACEMENT":
            displacement.append(item)
        elif result_name == "ENGINEERING_STRAIN_TENSOR":
            strain.append(item)
        elif result_name == "WATER_PRESSURE":
            water_pressure.append(item)

    def _is_tri3_element_gp(self, values: list) -> bool:
        return isinstance(values, list) and all(
            "value" in v and isinstance(v["value"], list) and len(v["value"]) == 3
            for v in values
        )

    def _first_value_or_none(self, result: dict) -> list | None:
        if result.get("values"):
            return result["values"][0]["value"][0]
        return None

    def _extract_stress_tensors(self, stress_results: list[dict]) -> dict:
        reshaped = {}
        for result in stress_results:
            time_step = result["time"]
            values = result["values"]
            if not values:
                continue
            sublist = self._first_value_or_none(result)
            if sublist is None:
                continue
            tensor = np.array(
                [
                    [sublist[0], sublist[3], sublist[5]],
                    [sublist[3], sublist[1], sublist[4]],
                    [sublist[5], sublist[4], sublist[2]],
                ]
            )
            if time_step not in reshaped:
                reshaped[time_step] = []
            reshaped[time_step].append(tensor)
        return reshaped

    def _extract_shear_stress_xy(self, stress_results: list[dict]) -> list[float]:
        shear_stress_xy = []
        for result in stress_results:
            values = result["values"]
            if not values:
                continue
            stress_components = self._first_value_or_none(result)
            if stress_components is None:
                continue
            shear_xy = stress_components[3]
            shear_stress_xy.append(shear_xy)
        return shear_stress_xy

    def _compute_strains(
        self, strain_results: list[dict]
    ) -> tuple[list[float], list[float], list[float], list[float], list[float], list[float]]:
        xx, yy, zz, xy, vol, shear_xy_util = [], [], [], [], [], []
        for result in strain_results:
            values = result["values"]
            if not values:
                continue
            first_value = self._first_value_or_none(result)
            if first_value is None:
                continue
            eps_xx, eps_yy, eps_zz, eps_xy = first_value[:4]
            xx.append(eps_xx)
            yy.append(eps_yy)
            zz.append(eps_zz)
            xy.append(eps_xy)
            vol.append(eps_xx + eps_yy + eps_zz)
            yy.append(eps_yy)
            shear_xy_util.append(eps_xy)
        return xx, yy, zz, xy, vol, shear_xy_util

    def _compute_scalar_stresses(self, results):
        return [r["values"][0]["value"][1] for r in results if r["values"]]

    def _extract_sigma_xx_yy(
        self, stress_results: list[dict]
    ) -> tuple[list[float], list[float]]:
        sigma_xx, sigma_yy = [], []
        for result in stress_results:
            stress_vec = self._first_value_or_none(result)
            if stress_vec is not None:
                sigma_xx.append(stress_vec[0])
                sigma_yy.append(stress_vec[1])

        return sigma_xx, sigma_yy

    def _apply_cumulative_strain_offset(
        self, strain_stages: list[list[float]]
    ) -> list[float]:
        cumulative = 0.0
        combined = []

        for stage in strain_stages:
            adjusted = [val + cumulative for val in stage]
            if adjusted:
                cumulative = adjusted[-1]
            combined.extend(adjusted)

        return combined

    def _extract_water_pressure(
        self, water_pressure_results: list[dict]
    ) -> list[float]:
        pressure_values = []
        for result in water_pressure_results:
            values = result["values"]
            if not values:
                continue

            val_container = values[0]["value"]
            if isinstance(val_container, list):
                if len(val_container) >= 1:
                    pressure_values.append(val_container[0])
            else:
                pressure_values.append(val_container)

        return pressure_values

    @staticmethod
    def _calculate_principal_stresses(
        tensors: Dict[float, List[np.ndarray]],
    ) -> Tuple[List[float], List[float]]:
        sigma_1, sigma_3 = [], []
        for time in sorted(tensors.keys()):
            for sigma in tensors[time]:
                eigenvalues, _ = np.linalg.eigh(sigma)
                sigma_1.append(float(np.min(eigenvalues)))
                sigma_3.append(float(np.max(eigenvalues)))
        return sigma_1, sigma_3

    @staticmethod
    def _calculate_principal_strains(
            xx: List[float], yy: List[float], zz: List[float], xy: List[float]
    ) -> List[float]:
        epsilon_1 = []
        # Calculate eigenvalues for each step
        # Tensor is [[xx, xy, 0], [xy, yy, 0], [0, 0, zz]]
        # Or just 2D eigs of [[xx, xy], [xy, yy]] and compare with zz?
        # Usually first principal strain is the most positive (tensile) or max?
        # In soil mechanics compressive is usually positive, but Kratos uses standard mechanics (tensile +).
        # We want the 'Major' principal strain.
        # sigma_1 is Min (most compressive) in the code below?
        # Line 270: sigma_1.append(float(np.min(eigenvalues)))
        # So sigma_1 is compressive stress (if compressive is negative).
        # Wait, Soil mechanics: Compressive stress is positive.
        # But `np.min` suggests negative values are large compression?
        # Let's stick to standard eigenvalue logic:
        # We return the "First Principal Strain". Usually implies the largest algebraic value (tension) or largest magnitude?
        # User definition: "first principal strain or the normal strain (epsilon 1) ... quantifying elongation or contraction"
        # Standard: e1 > e2 > e3.
        # The user seems to imply the vertical strain analog. In Triaxial (compression), vertical is epsilon 1 if we talk about magnitude of compression?
        # Let's assume standard math definition: e1 is max eigenvalue.

        for ex, ey, ez, exy in zip(xx, yy, zz, xy):
            # 3D Tensor approximation for available components
            tensor = np.array([
                [ex, exy, 0.0],
                [exy, ey, 0.0],
                [0.0, 0.0, ez]
            ])
            eigenvalues, _ = np.linalg.eigh(tensor)
            # Principal strains sort from min to max.
            # e1 usually max.
            # But earlier sigma_1 was min?
            # User wants "First Principal Strain (epsilon 1)".
            # I will return the Maximum eigenvalue (most positive / least compressive).
            # Unless they mean Major Principal Strain in terms of Compression?
            # Given text "elongation or contraction", it sounds generic.
            # I'll return the standard max eigenvalue.
            epsilon_1.append(float(np.max(eigenvalues)))

        return epsilon_1
