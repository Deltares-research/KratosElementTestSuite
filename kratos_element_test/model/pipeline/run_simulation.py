# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import json
import shutil
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
from kratos_element_test.model.core_utils import _fallback_log
from kratos_element_test.model.io.material_editor import MaterialEditor
from kratos_element_test.model.io.project_parameter_editor import ProjectParameterEditor
from kratos_element_test.model.io.mdpa_editor import MdpaEditor
from kratos_element_test.model.pipeline.generic_test_runner import GenericTestRunner
from kratos_element_test.model.pipeline.result_collector import ResultCollector

try:
    from importlib.resources import files as _res_files
except Exception:
    _res_files = None

REQUIRED_FILES = [
    "MaterialParameters.json",
    "mesh.mdpa",
    "ProjectParameters.json",
    "ProjectParametersOrchestrator.json",
]


class RunSimulation:
    def __init__(
        self,
        *,
        test_type: str,
        dll_path: Optional[str],
        udsm_number: Optional[int],
        material_parameters: List[float],
        num_steps: int | List[int],
        end_time: float,
        maximum_strain: float,
        initial_effective_cell_pressure: float,
        cohesion_phi_indices: Optional[Tuple[int, int]] = None,
        logger: Optional[Callable[[str, str], None]] = None,
        drainage: Optional[str] = None,
        stage_durations: Optional[List[float]] = None,
        step_counts: Optional[List[int]] = None,
        strain_incs: Optional[List[float]] = None,
        keep_tmp: bool = False,
    ):
        self.test_type = test_type.lower()
        self.dll_path = dll_path
        self.udsm_number = udsm_number
        self.material_parameters = material_parameters
        self.num_steps = num_steps
        self.end_time = end_time
        self.maximum_strain = maximum_strain
        self.initial_effective_cell_pressure = initial_effective_cell_pressure
        self.cohesion_phi_indices = cohesion_phi_indices
        self.log = logger or _fallback_log
        self.drainage = drainage
        self.stage_durations = stage_durations
        self.step_counts = step_counts
        self.strain_incs = strain_incs
        self.keep_tmp = keep_tmp

        self.tmp_dir = Path(tempfile.mkdtemp(prefix=f"{self.test_type}_"))
        self.material_json_path: Optional[Path] = None
        self.project_json_path: Optional[Path] = None
        self.mdpa_path: Optional[Path] = None

    def run(self) -> None:
        self.log(f"Starting {self.test_type} simulation...", "info")

        self._copy_simulation_files()

        if self.test_type == "crs":
            self._prepare_crs_stages()

        self._set_material_constitutive_law()
        self._set_project_parameters()
        self._set_mdpa()

        output_file_strings = [str(p) for p in self._output_file_paths()]
        runner = GenericTestRunner(output_file_strings, str(self.tmp_dir))
        runner.run()

        self.log("Finished analysis", "info")

    def post_process_results(self) -> Dict[str, List[float]]:
        try:
            self.log("Collecting results...", "info")

            output_file_strings = [str(p) for p in self._output_file_paths()]
            collector = ResultCollector(
                output_file_strings, self.material_parameters, self.cohesion_phi_indices
            )
            results = collector.collect_results()
            self.log("Rendering complete.", "info")
            return results

        finally:
            if self.keep_tmp:
                print(f"[Info] Temporary folder retained at: {self.tmp_dir}")
            else:
                try:
                    shutil.rmtree(self.tmp_dir, ignore_errors=True)
                    pass
                except Exception as e:
                    self.log(f"Failed to clean tmp dir: {e}", "warn")

    @staticmethod
    def _candidate_template_dirs(test_type: str) -> List[Path]:
        here = Path(__file__).resolve()
        candidates = [
            here.parent / f"test_{test_type}",  # legacy: alongside run_simulation.py
            here.parents[1]
            / "templates"
            / f"test_{test_type}",  # NEW: model/templates/test_*
            here.parents[1] / f"test_{test_type}",  # legacy: under model/
            here.parents[2] / f"test_{test_type}",  # legacy: under project root
        ]
        if _res_files:
            try:
                pkg_path = (
                    _res_files("kratos_element_test.model.templates")
                    / f"test_{test_type}"
                )
                candidates.append(Path(str(pkg_path)))
            except Exception:
                pass
        return candidates

    @classmethod
    def _find_template_dir(cls, test_type: str) -> Path:
        for p in cls._candidate_template_dirs(test_type):
            if p.exists():
                return p
        raise FileNotFoundError(
            f"Could not locate templates for '{test_type}'."
            f"Tried:\n  - " + "\n  - ".join(cls._candidate_template_dirs(test_type))
        )

    def _copy_simulation_files(self) -> None:
        src_dir = self._find_template_dir(self.test_type)
        copied = {}
        for filename in REQUIRED_FILES:
            src_file = src_dir / filename
            dst_file = self.tmp_dir / filename
            if src_file.exists():
                shutil.copy(src_file, dst_file)
                copied[filename] = dst_file

        if "ProjectParametersOrchestrator.json" in copied:
            self.project_json_path = copied["ProjectParametersOrchestrator.json"]
        elif "ProjectParameters.json" in copied:
            self.project_json_path = copied["ProjectParameters.json"]
        else:
            raise FileNotFoundError(
                "Neither ProjectParametersOrchestrator.json nor ProjectParameters.json found in template."
            )

        self.material_json_path = copied.get("MaterialParameters.json")
        self.mdpa_path = copied.get("mesh.mdpa")
        if self.mdpa_path is None:
            raise FileNotFoundError("mesh.mdpa missing in template set.")

    def _prepare_crs_stages(self) -> None:
        if not self.stage_durations or not self.step_counts:
            raise ValueError(
                "CRS test requires both stage durations and step counts to be provided."
            )

        editor = ProjectParameterEditor(str(self.project_json_path))
        data = json.load(open(self.project_json_path, "r"))
        current_stages = len(data.get("stages", {}))
        required_stages = len(self.stage_durations)

        if required_stages > current_stages:
            for d, s in zip(
                self.stage_durations[current_stages:], self.step_counts[current_stages:]
            ):
                editor.append_stage(duration=d, steps=s)

    def _set_material_constitutive_law(self) -> None:
        editor = MaterialEditor(str(self.material_json_path))
        if self.dll_path:
            editor.update_material_properties(
                {
                    "IS_FORTRAN_UDSM": True,
                    "UMAT_PARAMETERS": self.material_parameters,
                    "UDSM_NAME": self.dll_path,
                    "UDSM_NUMBER": self.udsm_number,
                }
            )
            editor.set_constitutive_law("SmallStrainUDSM2DPlaneStrainLaw")
        else:
            editor.update_material_properties(
                {
                    "YOUNG_MODULUS": self.material_parameters[0],
                    "POISSON_RATIO": self.material_parameters[1],
                }
            )
            editor.set_constitutive_law("GeoLinearElasticPlaneStrain2DLaw")

    def _set_project_parameters(self) -> None:
        with open(self.project_json_path, "r") as f:
            data = json.load(f)

        editor = ProjectParameterEditor(str(self.project_json_path))

        if "stages" in data:
            if self.stage_durations and isinstance(self.num_steps, list):
                if len(self.stage_durations) != len(self.num_steps):
                    raise ValueError(
                        f"Mismatch: {len(self.stage_durations)} stage durations but {len(self.num_steps)} step counts provided."
                    )

                cumulative_end_times = []
                total = 0.0
                for d in self.stage_durations:
                    total += d
                    cumulative_end_times.append(total)

                editor.update_stage_timings(
                    cumulative_end_times, self.num_steps, start_time=0.0
                )

                if len(cumulative_end_times) > 1:
                    editor.update_top_displacement_table_numbers()
        else:
            time_step = (
                (self.stage_durations[0] / self.num_steps[0])
                if (isinstance(self.num_steps, list) and self.stage_durations)
                else (self.end_time / self.num_steps)
            )
            editor.update_property("time_step", time_step)
            editor.update_property("end_time", self.end_time)

        # initial stress vector [-σ, -σ, -σ, 0]
        stress_vector = [-self.initial_effective_cell_pressure] * 3 + [0.0]
        editor.update_nested_value(
            "apply_initial_uniform_stress_field", "value", stress_vector
        )

    def _set_mdpa(self) -> None:
        editor = MdpaEditor(str(self.mdpa_path))
        editor.update_maximum_strain(self.maximum_strain)
        editor.update_end_time(self.end_time)

        if isinstance(self.num_steps, list) and self.stage_durations:
            first_timestep = self.stage_durations[0] / self.num_steps[0]
        else:
            first_timestep = self.end_time / self.num_steps
        editor.update_first_timestep(first_timestep)

        if self.test_type == "triaxial":
            editor.update_initial_effective_cell_pressure(
                self.initial_effective_cell_pressure
            )
        if self.test_type == "direct_shear":
            editor.update_middle_maximum_strain(self.maximum_strain)
        if self.test_type == "crs" and self.strain_incs and self.stage_durations:
            editor.insert_displacement_tables(self.stage_durations, self.strain_incs)
            editor.update_top_displacement_tables(len(self.stage_durations))

    def _output_file_paths(self) -> List[Path]:
        with open(self.project_json_path, "r") as f:
            project_data = json.load(f)

        if "stages" in project_data:
            return [
                self.tmp_dir / "gid_output" / f"output_stage{i + 1}.post.res"
                for i in range(len(project_data["stages"]))
            ]
        return [self.tmp_dir / "gid_output" / "output.post.res"]
