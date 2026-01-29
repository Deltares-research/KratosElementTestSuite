from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from kratos_element_test.model.core_utils import seconds_to_hours
from kratos_element_test.view.ui_logger import log_message as fallback_log
from KratosMultiphysics.GeoMechanicsApplication.gid_output_file_reader import (
    GiDOutputFileReader,
)


class ResultCollector:
    def __init__(
        self, output_file_paths, cohesion=None, phi=None, logger=None
    ):
        self.output_file_paths = output_file_paths
        self._log = logger or fallback_log
        self.cohesion=cohesion
        self.phi=phi

    def collect_results(self):
        all_tensors = {}
        yy_strain_stages = []
        all_shear_stress_xy = []
        all_vol_strain = []
        all_shear_strain_xy = []
        all_von_mises = []
        all_mean_stress = []
        all_sigma_xx = []
        all_sigma_yy = []
        all_time_steps = []

        for result_path in self.output_file_paths:
            s, ms, vm, d, e, t = self._read_results(result_path)

            tensors = self._extract_stress_tensors(s)
            shear_stress_xy = self._extract_shear_stress_xy(s)
            yy_strain, vol_strain, shear_strain_xy = self._compute_strains(e)
            von_mises_values = self._compute_scalar_stresses(vm)
            mean_stress_values = self._compute_scalar_stresses(ms)
            sigma_xx, sigma_yy = self._extract_sigma_xx_yy(s)
            time_steps = t

            for time, tensor_list in tensors.items():
                all_tensors.setdefault(time, []).extend(tensor_list)

            all_shear_stress_xy.extend(shear_stress_xy)
            yy_strain_stages.append(yy_strain)
            all_vol_strain.extend(vol_strain)
            all_shear_strain_xy.extend(shear_strain_xy)
            all_von_mises.extend(von_mises_values)
            all_mean_stress.extend(mean_stress_values)
            all_sigma_xx.extend(sigma_xx)
            all_sigma_yy.extend(sigma_yy)
            all_time_steps.extend([seconds_to_hours(t) for t in time_steps])

        all_yy_strain = self._apply_cumulative_strain_offset(yy_strain_stages)

        sigma_1, sigma_3 = self._calculate_principal_stresses(all_tensors)

        return {
            "yy_strain": all_yy_strain,
            "vol_strain": all_vol_strain,
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
        }

    def _read_output(self, result_path: Path) -> dict:
        return GiDOutputFileReader().read_output_from(result_path)

    def _read_results(self, result_path: Path):
        result_path = Path(result_path)
        stress, mean_stress, von_mises, displacement, strain, time_steps = (
            [],
            [],
            [],
            [],
            [],
            [],
        )

        if not result_path.exists():
            self._log(f"Missing result file: {result_path}", "warn")
            return stress, mean_stress, von_mises, displacement, strain, time_steps

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
                )

        time_steps = GiDOutputFileReader.get_time_steps_from_first_valid_result(output)

        return stress, mean_stress, von_mises, displacement, strain, time_steps

    def _categorize_result(
        self, result_name, item, stress, mean_stress, von_mises, displacement, strain
    ):
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
    ) -> tuple[list[float], list[float], list[float]]:
        yy, vol, shear_xy = [], [], []
        for result in strain_results:
            values = result["values"]
            if not values:
                continue
            first_value = self._first_value_or_none(result)
            if first_value is None:
                continue
            eps_xx, eps_yy, eps_zz, eps_xy = first_value[:4]
            vol.append(eps_xx + eps_yy + eps_zz)
            yy.append(eps_yy)
            shear_xy.append(eps_xy)
        return yy, vol, shear_xy

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
