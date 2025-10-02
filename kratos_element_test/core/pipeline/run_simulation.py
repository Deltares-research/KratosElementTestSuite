# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import json
import shutil
import tempfile
import numpy as np
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
from kratos_element_test.core.core_utils import _fallback_log
from kratos_element_test.core.io.material_editor import MaterialEditor
from kratos_element_test.core.io.project_parameter_editor import ProjectParameterEditor
from kratos_element_test.core.io.mdpa_editor import MdpaEditor
from kratos_element_test.core.pipeline.generic_test_runner import GenericTestRunner

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


class _NoOpPlotter:
    def triaxial(self, *args, **kwargs):
        pass

    def direct_shear(self, *args, **kwargs):
        pass

    def crs(self, *args, **kwargs):
        pass


class RunSimulation:
    def __init__(
        self,
        *,
        test_type: str,
        dll_path: Optional[str],
        index: Optional[int],
        material_parameters: List[float],
        num_steps: int | List[int],
        end_time: float,
        maximum_strain: float,
        initial_effective_cell_pressure: float,
        cohesion_phi_indices: Optional[Tuple[int, int]] = None,
        plotter=None,
        logger: Optional[Callable[[str, str], None]] = None,
        drainage: Optional[str] = None,
        stage_durations: Optional[List[float]] = None,
        step_counts: Optional[List[int]] = None,
        strain_incs: Optional[List[float]] = None,
        keep_tmp: bool = False,
    ):
        self.test_type = test_type.lower()
        self.dll_path = dll_path
        self.index = index
        self.material_parameters = material_parameters
        self.num_steps = num_steps
        self.end_time = end_time
        self.maximum_strain = maximum_strain
        self.initial_effective_cell_pressure = initial_effective_cell_pressure
        self.cohesion_phi_indices = cohesion_phi_indices
        self.plotter = plotter or _NoOpPlotter()
        self.log = logger or _fallback_log
        self.drainage = drainage
        self.stage_durations = stage_durations
        self.step_counts = step_counts
        self.strain_incs = strain_incs
        self.keep_tmp = keep_tmp

        self.tmp_dir = Path(tempfile.mkdtemp(prefix=f"{self.test_type}_"))
        self.material_json: Optional[Path] = None
        self.project_json: Optional[Path] = None
        self.mdpa_path: Optional[Path] = None

    def run(self) -> Dict[str, List[float]]:
        self.log(f"Starting {self.test_type} simulation...", "info")

        try:
            self._copy_simulation_files()

            if self.test_type == "crs":
                self._prepare_crs_stages()

            self._set_material_constitutive_law()
            self._set_project_parameters()
            self._set_mdpa()

            output_files = self._output_file_paths()
            runner = GenericTestRunner([str(p) for p in output_files], str(self.tmp_dir))

            (tensors, yy_strain, vol_strain, von_mises, mean_stress,
             shear_xy, shear_strain_xy, sigma_xx, sigma_yy, time_steps) = runner.run()

            self.log("Finished analysis; collecting results...", "info")

            sigma_1, sigma_3 = self._calculate_principal_stresses(tensors)
            cohesion, phi = self._get_cohesion_phi(self.material_parameters, self.cohesion_phi_indices)

            results = {
                "yy_strain": yy_strain,
                "vol_strain": vol_strain,
                "sigma1": sigma_1,
                "sigma3": sigma_3,
                "shear_xy": shear_xy,
                "shear_strain_xy": shear_strain_xy,
                "mean_stress": mean_stress,
                "von_mises": von_mises,
                "cohesion": cohesion,
                "phi": phi,
                "sigma_xx": sigma_xx,
                "sigma_yy": sigma_yy,
                "time_steps": time_steps,
            }

            self._render(results)
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
            here.parents[1] / "templates" / f"test_{test_type}",  # NEW: core/templates/test_*
            here.parents[1] / f"test_{test_type}",  # legacy: under core/
            here.parents[2] / f"test_{test_type}",  # legacy: under project root
        ]
        if _res_files:
            try:
                pkg_path = _res_files("kratos_element_test.core.templates") / f"test_{test_type}"
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
            self.project_json = copied["ProjectParametersOrchestrator.json"]
        elif "ProjectParameters.json" in copied:
            self.project_json = copied["ProjectParameters.json"]
        else:
            raise FileNotFoundError(
                "Neither ProjectParametersOrchestrator.json nor ProjectParameters.json found in template."
            )

        self.material_json = copied.get("MaterialParameters.json")
        self.mdpa_path = copied.get("mesh.mdpa")
        if self.mdpa_path is None:
            raise FileNotFoundError("mesh.mdpa missing in template set.")

    def _prepare_crs_stages(self) -> None:
        if not (self.stage_durations and self.step_counts):
            return

        editor = ProjectParameterEditor(str(self.project_json))
        data = json.load(open(self.project_json, "r"))
        current_stages = len(data.get("stages", {}))
        required_stages = len(self.stage_durations)

        if required_stages > current_stages:
            for d, s in zip(self.stage_durations[current_stages:], self.step_counts[current_stages:]):
                editor.append_stage(duration=d, steps=s)

    def _set_material_constitutive_law(self) -> None:
        editor = MaterialEditor(str(self.material_json))
        if self.dll_path:
            editor.update_material_properties({
                "IS_FORTRAN_UDSM": True,
                "UMAT_PARAMETERS": self.material_parameters,
                "UDSM_NAME": self.dll_path,
                "UDSM_NUMBER": self.index,
            })
            editor.set_constitutive_law("SmallStrainUDSM2DPlaneStrainLaw")
        else:
            editor.update_material_properties({
                "YOUNG_MODULUS": self.material_parameters[0],
                "POISSON_RATIO": self.material_parameters[1],
            })
            editor.set_constitutive_law("GeoLinearElasticPlaneStrain2DLaw")

    def _set_project_parameters(self) -> None:
        with open(self.project_json, "r") as f:
            data = json.load(f)

        editor = ProjectParameterEditor(str(self.project_json))

        if "stages" in data:
            if self.stage_durations and isinstance(self.num_steps, list):
                cumulative_end_times = []
                total = 0.0
                for d in self.stage_durations:
                    total += d
                    cumulative_end_times.append(total)

                editor.update_stage_timings(cumulative_end_times, self.num_steps, start_time=0.0)

                if len(cumulative_end_times) > 1:
                    editor.update_top_displacement_table_numbers()
            else:
                editor.update_stage_timings([self.end_time], self.num_steps, start_time=0.0)
        else:
            time_step = (self.stage_durations[0] / self.num_steps[0]) if (
                        isinstance(self.num_steps, list) and self.stage_durations) else (self.end_time / self.num_steps)
            editor.update_property('time_step', time_step)
            editor.update_property('end_time', self.end_time)

        # initial stress vector [-σ, -σ, -σ, 0]
        stress_vector = [-self.initial_effective_cell_pressure] * 3 + [0.0]
        editor.update_nested_value("apply_initial_uniform_stress_field", "value", stress_vector)

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
            editor.update_initial_effective_cell_pressure(self.initial_effective_cell_pressure)
        if self.test_type == "direct_shear":
            editor.update_middle_maximum_strain(self.maximum_strain)
        if self.test_type == "crs" and self.strain_incs and self.stage_durations:
            editor.insert_displacement_tables(self.stage_durations, self.strain_incs)
            editor.update_top_displacement_tables(len(self.stage_durations))

    def _output_file_paths(self) -> List[Path]:
        with open(self.project_json, "r") as f:
            project_data = json.load(f)

        if "stages" in project_data:
            return [
                self.tmp_dir / "gid_output" / f"output_stage{i + 1}.post.res"
                for i in range(len(project_data["stages"]))
            ]
        return [self.tmp_dir / "gid_output" / "output.post.res"]

    @staticmethod
    def _calculate_principal_stresses(tensors: Dict[float, List[np.ndarray]]) -> Tuple[List[float], List[float]]:
        sigma_1, sigma_3 = [], []
        for time in sorted(tensors.keys()):
            for sigma in tensors[time]:
                eigenvalues, _ = np.linalg.eigh(sigma)
                sigma_1.append(float(np.min(eigenvalues)))
                sigma_3.append(float(np.max(eigenvalues)))
        return sigma_1, sigma_3

    @staticmethod
    def _get_cohesion_phi(umat_parameters: List[float], indices: Optional[Tuple[int, int]]) -> Tuple[
            Optional[float], Optional[float]]:
        if not indices:
            return None, None
        c_idx, phi_idx = indices
        return float(umat_parameters[c_idx - 1]), float(umat_parameters[phi_idx - 1])

    def _render(self, results: Dict[str, List[float]]) -> None:
        if not self.plotter:
            self.log('No plotter was provided; using a no-op plotter (headless run).', 'info')
            return

        if self.test_type == "triaxial":
            self.plotter.triaxial(
                results["yy_strain"], results["vol_strain"],
                results["sigma1"], results["sigma3"],
                results["mean_stress"], results["von_mises"],
                results["cohesion"], results["phi"],
            )
        elif self.test_type == "direct_shear":
            self.plotter.direct_shear(
                results["shear_strain_xy"], results["shear_xy"],
                results["sigma1"], results["sigma3"],
                results["mean_stress"], results["von_mises"],
                results["cohesion"], results["phi"],
            )
        elif self.test_type == "crs":
            self.plotter.crs(
                results["yy_strain"], results["time_steps"],
                results["sigma_yy"], results["sigma_xx"],
                results["mean_stress"], results["von_mises"],
                results["sigma1"], results["sigma3"],
                results["cohesion"], results["phi"],
            )
        else:
            raise ValueError(f"Unsupported test_type: {self.test_type}")

    def run_simulation(**kwargs):
        return RunSimulation(**kwargs).run()
