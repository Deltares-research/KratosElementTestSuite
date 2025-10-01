# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import os
import json
import importlib
import numpy as np
from pathlib import Path
import KratosMultiphysics as Kratos
from KratosMultiphysics.GeoMechanicsApplication.geomechanics_analysis import GeoMechanicsAnalysis
from KratosMultiphysics.project import Project
from kratos_element_test.core.io import gid_output_reader
from kratos_element_test.ui.ui_logger import log_message as fallback_log
import KratosMultiphysics.GeoMechanicsApplication.context_managers as context_managers


class GenericTestRunner:
    def __init__(self, output_file_paths, work_dir, logger=None):
        self.output_file_paths = output_file_paths
        self.work_dir = work_dir
        self._log = logger or fallback_log

    def run(self):
        use_orchestrator = self._has_orchestrator()
        self._log(f"work_dir={os.path.abspath(self.work_dir)} | orchestrator={use_orchestrator}", "info")
        if use_orchestrator:
            self._run_orchestrator()
        else:
            parameters = self._load_stage_parameters()
            self._execute_analysis_stages(parameters)

        all_tensors = {}
        yy_strain_stages = []
        all_shear_stress_xy = []
        all_yy_strain = []
        all_vol_strain = []
        all_shear_strain_xy = []
        all_von_mises = []
        all_mean_stress = []
        all_sigma_xx = []
        all_sigma_yy = []
        all_time_steps = []

        for result_path in self.output_file_paths:
            s, ms, vm, d, e, t = self._collect_results(result_path)

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
            all_time_steps.extend([t / 3600.0 for t in time_steps])  # Convert seconds → hours

            all_yy_strain = self._apply_cumulative_strain_offset(yy_strain_stages)

        return (
            all_tensors,
            all_yy_strain,
            all_vol_strain,
            all_von_mises,
            all_mean_stress,
            all_shear_stress_xy,
            all_shear_strain_xy,
            all_sigma_xx,
            all_sigma_yy,
            all_time_steps
        )

    def _load_kratos_parameters_from_file(self, json_path: str) -> Kratos.Parameters:
        with open(json_path, "r") as f:
            return Kratos.Parameters(f.read())

    def _load_stage_parameters(self):
        orch_path = os.path.join(self.work_dir, "ProjectParametersOrchestrator.json")
        legacy_path = os.path.join(self.work_dir, "ProjectParameters.json")

        if os.path.exists(orch_path):
            return [self._load_kratos_parameters_from_file(orch_path)]

        if os.path.exists(legacy_path):
            return [self._load_kratos_parameters_from_file(legacy_path)]

        raise FileNotFoundError("Neither ProjectParametersOrchestrator.json nor ProjectParameters.json found.")

    def _execute_analysis_stages(self, parameters):
        model = Kratos.Model()
        stages = [GeoMechanicsAnalysis(model, p) for p in parameters]
        original_cwd = os.getcwd()
        try:
            os.chdir(self.work_dir)
            for stage in stages:
                stage.Run()
        finally:
            os.chdir(original_cwd)

    def _read_output(self, result_path: Path) -> dict:
        output = gid_output_reader.GiDOutputFileReader().read_output_from(result_path)
        return output

    def _collect_results(self, result_path: Path):
        result_path = Path(result_path)
        stress, mean_stress, von_mises, displacement, strain, time_steps = [], [], [], [], [], []

        if not result_path.exists():
            self._log(f"Missing result file: {result_path}", "warn")
            return stress, mean_stress, von_mises, displacement, strain, time_steps

        output = self._read_output(result_path)

        for result_name, items in output.get("results", {}).items():
            for item in items:
                self._categorize_result(result_name, item, stress, mean_stress, von_mises, displacement, strain)

        time_steps = gid_output_reader.GiDOutputFileReader.get_time_steps_from_first_valid_result(output)

        return stress, mean_stress, von_mises, displacement, strain, time_steps

    def _categorize_result(self, result_name, item, stress, mean_stress, von_mises, displacement, strain):
        values = item["values"]
        if result_name == "CAUCHY_STRESS_TENSOR":
            stress.append(item)
        elif result_name == "MEAN_EFFECTIVE_STRESS" and self._is_tri3_element_gp(values):
            mean_stress.append(item)
        elif result_name == "VON_MISES_STRESS" and self._is_tri3_element_gp(values):
            von_mises.append(item)
        elif result_name == "DISPLACEMENT":
            displacement.append(item)
        elif result_name == "ENGINEERING_STRAIN_TENSOR":
            strain.append(item)

    def _is_tri3_element_gp(self, values: list) -> bool:
        return isinstance(values, list) and all("value" in v and isinstance(v["value"], list) and
                                                len(v["value"]) == 3 for v in values)

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
            tensor = np.array([
                [sublist[0], sublist[3], sublist[5]],
                [sublist[3], sublist[1], sublist[4]],
                [sublist[5], sublist[4], sublist[2]],
            ])
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
            shear_xy = stress_components[3]
            shear_stress_xy.append(shear_xy)
        return shear_stress_xy

    def _compute_strains(self, strain_results: list[dict]) -> tuple[list[float], list[float], list[float]]:
        yy, vol, shear_xy = [], [], []
        for result in strain_results:
            values = result["values"]
            if not values:
                continue
            eps_xx, eps_yy, eps_zz, eps_xy = self._first_value_or_none(result)[:4]
            vol.append(eps_xx + eps_yy + eps_zz)
            yy.append(eps_yy)
            shear_xy.append(eps_xy)
        return yy, vol, shear_xy

    def _compute_scalar_stresses(self, results):
        return [r["values"][0]["value"][1] for r in results if r["values"]]

    def _extract_sigma_xx_yy(self, stress_results: list[dict]) -> tuple[list[float], list[float]]:
        sigma_xx, sigma_yy = [], []
        for result in stress_results:
            stress_vec = self._first_value_or_none(result)
            if stress_vec is not None:
                sigma_xx.append(stress_vec[0])
                sigma_yy.append(stress_vec[1])

        return sigma_xx, sigma_yy

    def _apply_cumulative_strain_offset(self, strain_stages: list[list[float]]) -> list[float]:
        cumulative = 0.0
        combined = []

        for stage in strain_stages:
            adjusted = [val + cumulative for val in stage]
            if adjusted:
                cumulative = adjusted[-1]
            combined.extend(adjusted)

        return combined

    def _has_orchestrator(self):
        orch_candidates = [
            os.path.join(self.work_dir, "ProjectParametersOrchestrator.json"),
            os.path.join(os.getcwd(), "ProjectParametersOrchestrator.json"),
            os.path.join(self.work_dir, "ProjectParameters_Orchestrator.json"),
        ]

        if any(os.path.isfile(p) for p in orch_candidates):
            return True

        pp = os.path.join(self.work_dir, "ProjectParameters.json")
        if os.path.isfile(pp):
            try:
                with open(pp, "r") as f:
                    d = json.load(f)
                return isinstance(d, dict) and "orchestrator" in d and "stages" in d
            except Exception:
                pass
        return False

    def _run_orchestrator(self):
        params_path = os.path.join(self.work_dir, "ProjectParametersOrchestrator.json")
        if not os.path.exists(params_path):
            params_path = os.path.join(self.work_dir, "ProjectParameters.json")

        project = Project(self._load_kratos_parameters_from_file(params_path))

        orchestrator_name = project.GetSettings()["orchestrator"]["name"].GetString()
        reg_entry = Kratos.Registry[orchestrator_name]
        orchestrator_module = importlib.import_module(reg_entry["ModuleName"])
        orchestrator_class = getattr(orchestrator_module, reg_entry["ClassName"])

        with context_managers.set_cwd_to(self.work_dir):
            orchestrator_class(project).Run()
