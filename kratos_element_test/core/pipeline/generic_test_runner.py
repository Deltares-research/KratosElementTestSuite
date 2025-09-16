# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import re
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
        print(
        f"[GenericTestRunner] work_dir={os.path.abspath(self.work_dir)} | orchestrator={use_orchestrator}")
        if use_orchestrator:
            self._run_orchestrator()
        else:
            parameters = self._load_stage_parameters()
            self._execute_analysis_stages(parameters)

        stress, mean_stress, von_mises, _, strain = self._collect_results()
        tensors = self._extract_stress_tensors(stress)
        shear_stress_xy = self._extract_shear_stress_xy(stress)
        yy_strain, vol_strain, shear_strain_xy = self._compute_strains(strain)
        von_mises_values = self._compute_scalar_stresses(von_mises)
        mean_stress_values = self._compute_scalar_stresses(mean_stress)
        sigma_xx, sigma_yy = self._extract_sigma_xx_yy(stress)
        time_steps = self._extract_time_steps(strain)

        return (tensors, yy_strain, vol_strain, von_mises_values, mean_stress_values, shear_stress_xy, shear_strain_xy,
                sigma_xx, sigma_yy, time_steps)

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

    def _collect_results(self):
        stress, mean_stress, von_mises, displacement, strain = [], [], [], [], []
        base_path = Path(self.work_dir)

        all_results = []
        for result_path in self.output_file_paths:
            result_path = Path(result_path)
            if not result_path.exists():
                self._log(f"Missing result file: {result_path}", "warn")
                continue

            output = gid_output_reader.GiDOutputFileReader().read_output_from(result_path)
            self._log(f"Available result keys in {result_path.name}: {list(output.get('results', {}).keys())}", "info")
            self._log(f"Loaded {sum(len(v) for v in output.get('results', {}).values())} entries from: {result_path}",
                      "info")

            for result_name, items in output.get("results", {}).items():
                for item in items:
                    self._categorize_result(result_name, item, stress, mean_stress, von_mises, displacement, strain)

        self._log(f"Collected {len(stress)} stress, {len(mean_stress)} mean stress, "
                  f"{len(von_mises)} von mises, {len(strain)} strain entries", "info")

        return stress, mean_stress, von_mises, displacement, strain

    def _categorize_result(self, result_name, item, stress, mean_stress, von_mises, displacement, strain):
        values = item["values"]
        if result_name == "CAUCHY_STRESS_TENSOR":
            stress.append(item)
        elif result_name == "MEAN_EFFECTIVE_STRESS": #and self._is_tri3_element_gp(values):
            mean_stress.append(item)
        elif result_name == "VON_MISES_STRESS": #and self._is_tri3_element_gp(values):
            von_mises.append(item)
        elif result_name == "DISPLACEMENT":
            displacement.append(item)
        elif result_name == "ENGINEERING_STRAIN_TENSOR":
            strain.append(item)

    def _is_tri3_element_gp(self, values):
        return isinstance(values, list) and all("value" in v and isinstance(v["value"], list) and
                                                len(v["value"]) == 3 for v in values)

    def _extract_stress_tensors(self, stress_results):
        reshaped = {}
        for result in stress_results:
            time_step = result["time"]
            values = result["values"]
            if not values:
                continue
            sublist = values[0]["value"][0]
            tensor = np.array([
                [sublist[0], sublist[3], sublist[5]],
                [sublist[3], sublist[1], sublist[4]],
                [sublist[5], sublist[4], sublist[2]],
            ])
            if time_step not in reshaped:
                reshaped[time_step] = []
            reshaped[time_step].append(tensor)
            # reshaped[time_step] = [tensor]
        return reshaped

    def _extract_shear_stress_xy(self, stress_results):
        shear_stress_xy = []
        for result in stress_results:
            values = result["values"]
            if not values:
                continue
            stress_components = values[0]["value"][0]
            shear_xy = stress_components[3]
            shear_stress_xy.append(shear_xy)
        return shear_stress_xy

    def _extract_time_steps(self, strain_results):
        times = []
        for result in strain_results:
            values = result["values"]
            if not values:
                continue
            times.append(result["time"])
        return times

    def _compute_strains(self, strain_results):
        yy, vol, shear_xy = [], [], []
        for result in strain_results:
            values = result["values"]
            if not values:
                continue
            eps_xx, eps_yy, eps_zz, eps_xy = values[0]["value"][0][:4]
            vol.append(eps_xx + eps_yy + eps_zz)
            yy.append(eps_yy)
            shear_xy.append(eps_xy)
        return yy, vol, shear_xy

    def _compute_scalar_stresses(self, results):
        return [r["values"][0]["value"][1] for r in results if r["values"]]

    def _extract_sigma_xx_yy(self, stress_results):
        sigma_xx, sigma_yy= [], []

        for result in stress_results:
            values = result["values"]
            if not values:
                continue
            stress_vec = values[0]["value"][0]
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
