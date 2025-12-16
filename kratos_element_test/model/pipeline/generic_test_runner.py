# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import os
import json
import importlib
import KratosMultiphysics as Kratos
from KratosMultiphysics.GeoMechanicsApplication.geomechanics_analysis import GeoMechanicsAnalysis
from KratosMultiphysics.project import Project
from kratos_element_test.view.ui_logger import log_message as fallback_log
import KratosMultiphysics.GeoMechanicsApplication.context_managers as context_managers


class GenericTestRunner:
    def __init__(self, output_file_paths, work_dir, logger=None):
        self.output_file_paths = output_file_paths
        self.work_dir = work_dir
        self._log = logger or fallback_log

    def run(self):
        use_orchestrator = self._has_orchestrator()
        if use_orchestrator:
            self._run_orchestrator()
        else:
            parameters = self._load_stage_parameters()
            self._execute_analysis_stages(parameters)

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

    def _has_orchestrator(self):
        orchestrator_path = os.path.join(self.work_dir, "ProjectParametersOrchestrator.json")

        if os.path.isfile(orchestrator_path):
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
