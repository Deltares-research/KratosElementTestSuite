# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import os
import json
import shutil
import tempfile
import numpy as np
from pathlib import Path
from kratos_element_test.core.io.material_editor import MaterialEditor
from kratos_element_test.core.io.project_parameter_editor import ProjectParameterEditor
from kratos_element_test.core.io.mdpa_editor import MdpaEditor
from kratos_element_test.core.pipeline.generic_test_runner import GenericTestRunner

try:
    from importlib.resources import files as _res_files
except Exception:
    _res_files = None


class _NoOpPlotter:
    def triaxial(self, *args, **kwargs):
        pass

    def direct_shear(self, *args, **kwargs):
        pass

def _candidate_template_dirs(test_type: str):
    here = Path(__file__).resolve()
    candidates = [
        here.parent / f"test_{test_type}",                           # legacy: alongside run_simulation.py
        here.parents[1] / "templates" / f"test_{test_type}",         # NEW: core/templates/test_*
        here.parents[1] / f"test_{test_type}",                       # legacy: under core/
        here.parents[2] / f"test_{test_type}",                       # legacy: under project root
    ]
    if _res_files:
        try:
            pkg_path = _res_files("kratos_element_test.core.templates") / f"test_{test_type}"
            candidates.append(Path(str(pkg_path)))
        except Exception:
            pass
    return candidates

def _find_template_dir(test_type: str) -> Path:
    for p in _candidate_template_dirs(test_type):
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Could not locate templates for'{test_type}'."
        f"Tried:\n  - " + "\n  - ".join(_candidate_template_dirs(test_type))
    )

def setup_simulation_files(test_type, tmp_folder):
    src_dir = _find_template_dir(test_type)
    copied = {}
    for filename in ["MaterialParameters.json", "mesh.mdpa",
                     "ProjectParameters.json", "ProjectParametersOrchestrator.json"]:
        src_file = os.path.join(src_dir, filename)
        dst_file = os.path.join(tmp_folder, filename)
        if os.path.exists(src_file):
            shutil.copy(src_file, dst_file)
            copied[filename] = dst_file

    if "ProjectParametersOrchestrator.json" in copied:
        project_file = copied["ProjectParametersOrchestrator.json"]
    elif "ProjectParameters.json" in copied:
        project_file = copied["ProjectParameters.json"]
    else:
        raise FileNotFoundError(
            "Neither ProjectParametersOrchestrator.json nor ProjectParameters.json found in template.")

    return (
        copied.get("MaterialParameters.json"),
        project_file,
        copied.get("mesh.mdpa")
    )

def set_material_constitutive_law(json_file_path, dll_path, material_parameters, index):
    editor = MaterialEditor(json_file_path)
    if dll_path:
        editor.update_material_properties({
            "IS_FORTRAN_UDSM": True,
            "UMAT_PARAMETERS": material_parameters,
            "UDSM_NAME": dll_path,
            "UDSM_NUMBER": index
        })
        editor.set_constitutive_law("SmallStrainUDSM2DPlaneStrainLaw")
    else:
        editor.update_material_properties({
            "YOUNG_MODULUS": material_parameters[0],
            "POISSON_RATIO": material_parameters[1]
        })
        editor.set_constitutive_law("GeoLinearElasticPlaneStrain2DLaw")

def set_project_parameters(project_path, num_steps, end_time, initial_stress, stage_durations=None):
    with open(project_path, 'r') as f:
        data = json.load(f)

    editor = ProjectParameterEditor(project_path)
    if "stages" in data:
        num_stages = len(data["stages"])
        if stage_durations and isinstance(num_steps, list):
            cumulative_end_times = []
            total = 0.0
            for d in stage_durations:
                total += d
                cumulative_end_times.append(total)

            print("[DEBUG] cumulative_end_times =", cumulative_end_times)
            print("[DEBUG] num_steps per stage =", num_steps)

            editor.update_stage_timings(cumulative_end_times, num_steps)
        else:
            editor.update_stage_timings([end_time], num_steps)

    else:
        editor.update_property('time_step', end_time / num_steps)
        editor.update_property('end_time', end_time)

    stress_vector = [-initial_stress] * 3 + [0.0]
    editor.update_nested_value("apply_initial_uniform_stress_field", "value", stress_vector)

def set_mdpa(mdpa_path, max_strain, init_pressure, num_steps, first_timestep, end_time, test_type):
    editor = MdpaEditor(mdpa_path)
    editor.update_maximum_strain(max_strain)
    editor.update_end_time(end_time)
    editor.update_first_timestep(first_timestep)
    if test_type == "triaxial":
        editor.update_initial_effective_cell_pressure(init_pressure)
    if test_type == "direct_shear":
        editor.update_middle_maximum_strain(max_strain)
    if test_type == "crs":
        editor.update_middle_maximum_strain(max_strain)

def calculate_principal_stresses(tensors):
    sigma_1, sigma_3 = [], []
    for time in sorted(tensors.keys()):
        for sigma in tensors[time]:
            eigenvalues, _ = np.linalg.eigh(sigma)
            sigma_1.append(np.min(eigenvalues))
            sigma_3.append(np.max(eigenvalues))
    # for tensors_at_time in tensors.values():
    #     for sigma in tensors_at_time:
    #         eigenvalues, _ = np.linalg.eigh(sigma)
    #         sigma_1.append(np.min(eigenvalues))
    #         sigma_3.append(np.max(eigenvalues))
    return sigma_1, sigma_3

def get_cohesion_phi(umat_parameters, indices):
    if indices:
        c_idx, phi_idx = indices
        return float(umat_parameters[c_idx - 1]), float(umat_parameters[phi_idx - 1])
    return None, None

def _render_with_plotter(test_type, plotter, results):
    if plotter is None:
        return
    if test_type == "triaxial":
        plotter.triaxial(
            results["yy_strain"], results["vol_strain"],
            results["sigma_yy"], results["sigma_xx"],
            results["sigma1"], results["sigma3"],
            results["mean_stress"], results["von_mises"],
            results["cohesion"], results["phi"]
        )
    elif test_type == "direct_shear":
        plotter.direct_shear(
            results["shear_strain_xy"], results["shear_xy"],
            results["sigma1"], results["sigma3"],
            results["mean_stress"], results["von_mises"],
            results["cohesion"], results["phi"]
        )
    elif test_type == "crs":
        plotter.crs(
            results["yy_strain"], results["time_steps"],
            results["sigma_yy"], results["sigma_xx"],
            results["mean_stress"], results["von_mises"],
            results["sigma1"], results["sigma3"],
            results["cohesion"], results["phi"]
        )
    else:
        raise ValueError(f"Unsupported test_type: {test_type}")

def run_simulation(*, test_type: str, dll_path: str, index, material_parameters, num_steps, end_time,
                   maximum_strain, initial_effective_cell_pressure, cohesion_phi_indices=None,
                   plotter=None, logger=None, drainage: str | None = None, stage_durations: list[float] | None = None,
                   step_counts=list[int] | None , strain_incs: list[float] | None = None):

    log = logger or (lambda msg, level="info": None)
    tmp_folder = tempfile.mkdtemp(prefix=f"{test_type}_")

    try:
        log(f"Starting {test_type} simulation...", "info")
        json_path, orchestrator_path, mdpa_path = setup_simulation_files(test_type, tmp_folder)

        if os.path.exists(orchestrator_path):
            project_path = orchestrator_path
        else:
            raise FileNotFoundError(f"Expected project parameters file not found at: {orchestrator_path}")

        if test_type == "crs" and stage_durations and step_counts:
            editor = ProjectParameterEditor(project_path)
            for d, s in zip(stage_durations[2:], step_counts[2:]):
                editor.append_crs_stage(duration=d, steps=s)

        set_material_constitutive_law(json_path, dll_path, material_parameters, index)

        print("[DEBUG] run_simulation(): num_steps =", num_steps)
        print("[DEBUG] stage_durations =", stage_durations)
        print("[DEBUG] run_simulation(): strain_incs =", strain_incs)

        set_project_parameters(project_path, num_steps, end_time, initial_effective_cell_pressure, stage_durations)
        # set_mdpa(mdpa_path, maximum_strain, initial_effective_cell_pressure, num_steps, end_time, test_type)
        if isinstance(num_steps, list) and stage_durations:
            first_timestep = stage_durations[0] / num_steps[0]
        else:
            first_timestep = end_time / num_steps

        set_mdpa(mdpa_path, maximum_strain, initial_effective_cell_pressure, num_steps, first_timestep, end_time,
                 test_type, strain_incs, stage_durations)

        # runner = GenericTestRunner([os.path.join(tmp_folder, 'gid_output', "output.post.res")], tmp_folder)
        with open(project_path, 'r') as f:
            project_json = json.load(f)

        if "stages" in project_json:
            output_files = [
                os.path.join(tmp_folder, "gid_output", f"output_stage{i + 1}.post.res")
                for i in range(len(project_json["stages"]))
            ]
        else:
            output_files = [os.path.join(tmp_folder, "gid_output", "output.post.res")]

        runner = GenericTestRunner(output_files, tmp_folder)
        (tensors, yy_strain, vol_strain, von_mises, mean_stress, shear_xy, shear_strain_xy,
         sigma_xx, sigma_yy, time_steps) = runner.run()
        log("Finished analysis; collecting results...", "info")

        sigma_1, sigma_3 = calculate_principal_stresses(tensors)
        log(f"Principal stress count: sigma_1={len(sigma_1)}, sigma_3={len(sigma_3)}", "info")

        cohesion, friction_angle = get_cohesion_phi(material_parameters, cohesion_phi_indices)

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
            "phi": friction_angle,
            "sigma_xx": sigma_xx,
            "sigma_yy": sigma_yy,
            "time_steps": time_steps,
        }

        if plotter is None:
            log('No plotter was provided; using a no-op plotter (headless run).', 'info')
            plotter = _NoOpPlotter()

        _render_with_plotter(test_type, plotter, results)
        log("Rendering complete.", "info")
        return results

    finally:
        if os.path.exists(tmp_folder):
            #TODO:# shutil.rmtree(tmp_folder)
            print(f"[Info] Temporary folder retained at: {tmp_folder}")