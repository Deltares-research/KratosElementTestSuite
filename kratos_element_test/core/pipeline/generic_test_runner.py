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


class GenericTestRunner:
    def __init__(self, output_file_paths, work_dir, logger=None, plotter=None):
        self.output_file_paths = output_file_paths
        self.work_dir = work_dir
        self._orchestrator_params_path = None
        self._plotter = plotter
        self._log = logger or (lambda msg, lvl="info": print(f"[{lvl.upper()}] {msg}"))

    def run(self):
        use_orchestrator = self._has_orchestrator()
        self._log(f"work_dir={os.path.abspath(self.work_dir)} | orchestrator={use_orchestrator}", "info")
        if use_orchestrator:
            self._run_orchestrator()
        else:
            parameters = self._load_stage_parameters()
            self._execute_analysis_stages(parameters)

        # Initialize all result containers
        all_tensors = {}
        all_shear_stress_xy = []
        all_yy_strain = []
        all_vol_strain = []
        all_shear_strain_xy = []
        all_von_mises = []
        all_mean_stress = []
        all_sigma_xx = []
        all_sigma_yy = []
        all_time_steps = []

        cumulative_yy_strain = 0.0  # Shift amount for the next stage

        for result_path in self.output_file_paths:
            s, ms, vm, d, e, t = self._collect_results(result_path)

            tensors = self._extract_stress_tensors(s)
            shear_stress_xy = self._extract_shear_stress_xy(s)
            yy_strain, vol_strain, shear_strain_xy = self._compute_strains(e)
            von_mises_values = self._compute_scalar_stresses(vm)
            mean_stress_values = self._compute_scalar_stresses(ms)
            sigma_xx, sigma_yy = self._extract_sigma_xx_yy(s)
            time_steps = t

            # Adjust sigma_yy for cumulative behavior for CRS test
            if all_yy_strain:  # only apply offset if this is NOT the first stage
                yy_strain = [val + cumulative_yy_strain for val in yy_strain]

            # Update the cumulative offset (for next stage)
            if yy_strain:
                cumulative_yy_strain = yy_strain[-1]

            for time, tensor_list in tensors.items():
                all_tensors.setdefault(time, []).extend(tensor_list)

            all_shear_stress_xy.extend(shear_stress_xy)
            all_yy_strain.extend(yy_strain)
            all_vol_strain.extend(vol_strain)
            all_shear_strain_xy.extend(shear_strain_xy)
            all_von_mises.extend(von_mises_values)
            all_mean_stress.extend(mean_stress_values)
            all_sigma_xx.extend(sigma_xx)
            all_sigma_yy.extend(sigma_yy)
            all_time_steps.extend(time_steps)

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

    def _load_stage_parameters(self):
        orch_path = os.path.join(self.work_dir, "ProjectParametersOrchestrator.json")
        legacy_path = os.path.join(self.work_dir, "ProjectParameters.json")

        if os.path.exists(orch_path):
            with open(orch_path, "r") as f:
                return [Kratos.Parameters(f.read())]

        if os.path.exists(legacy_path):
            with open(legacy_path, "r") as f:
                return [Kratos.Parameters(f.read())]

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
        self._log(f"Available result keys in {result_path.name}: {list(output.get('results', {}).keys())}", "info")
        self._log(f"Loaded {sum(len(v) for v in output.get('results', {}).values())} entries from: {result_path}",
                  "info")
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

    def _is_tri3_element_gp(self, values):
        return isinstance(values, list) and all("value" in v and isinstance(v["value"], list) and
                                                len(v["value"]) == 3 for v in values)

    def _first_value_or_none(self, result: dict):
        if result.get("values"):
            return result["values"][0]["value"][0]
        return None

    def _extract_stress_tensors(self, stress_results):
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

    def _extract_shear_stress_xy(self, stress_results):
        shear_stress_xy = []
        for result in stress_results:
            values = result["values"]
            if not values:
                continue
            stress_components = self._first_value_or_none(result)
            shear_xy = stress_components[3]
            shear_stress_xy.append(shear_xy)
        return shear_stress_xy

    def _compute_strains(self, strain_results):
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

    def _extract_sigma_xx_yy(self, stress_results):
        sigma_xx, sigma_yy = [], []
        for result in stress_results:
            stress_vec = self._first_value_or_none(result)
            if stress_vec is not None:
                sigma_xx.append(stress_vec[0])
                sigma_yy.append(stress_vec[1])

        return sigma_xx, sigma_yy

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

        with open(params_path, "r") as parameter_file:
            project_parameters = Kratos.Parameters(parameter_file.read())
        project = Project(project_parameters)

        orchestrator_name = project.GetSettings()["orchestrator"]["name"].GetString()
        reg_entry = Kratos.Registry[orchestrator_name]
        orchestrator_module = importlib.import_module(reg_entry["ModuleName"])
        orchestrator_class = getattr(orchestrator_module, reg_entry["ClassName"])

        original_cwd = os.getcwd()

        try:
            os.chdir(self.work_dir)
            orchestrator_instance = orchestrator_class(project)
            orchestrator_instance.Run()
        finally:
            os.chdir(original_cwd)
