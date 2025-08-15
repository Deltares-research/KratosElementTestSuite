# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import os
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
    tried = []
    for p in _candidate_template_dirs(test_type):
        tried.append(str(p))
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Could not locate templates for '{test_type}'. Tried:\n  - " + "\n  - ".join(tried)
    )

def setup_simulation_files(test_type, tmp_folder):
    src_dir = _find_template_dir(test_type)
    for filename in ["MaterialParameters.json", "ProjectParameters.json", "mesh.mdpa"]:
        shutil.copy(os.path.join(src_dir, filename), tmp_folder)
    return (
        os.path.join(tmp_folder, "MaterialParameters.json"),
        os.path.join(tmp_folder, "ProjectParameters.json"),
        os.path.join(tmp_folder, "mesh.mdpa")
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

def set_project_parameters(project_path, num_steps, end_time, initial_stress):
    editor = ProjectParameterEditor(project_path)
    editor.update_property('time_step', end_time / num_steps)
    editor.update_property('end_time', end_time)
    stress_vector = [-initial_stress] * 3 + [0.0]
    editor.update_nested_value("apply_initial_uniform_stress_field", "value", stress_vector)

def set_mdpa(mdpa_path, max_strain, init_pressure, num_steps, end_time, test_type):
    editor = MdpaEditor(mdpa_path)
    editor.update_maximum_strain(max_strain)
    editor.update_end_time(end_time)
    editor.update_first_timestep(num_steps, end_time)
    if test_type == "triaxial":
        editor.update_initial_effective_cell_pressure(init_pressure)
    if test_type == "direct_shear":
        editor.update_middle_maximum_strain(max_strain)

def calculate_principal_stresses(tensors):
    sigma_1, sigma_3 = [], []
    for tensors_at_time in tensors.values():
        for sigma in tensors_at_time:
            eigenvalues, _ = np.linalg.eigh(sigma)
            sigma_1.append(np.min(eigenvalues))
            sigma_3.append(np.max(eigenvalues))
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
    else:
        raise ValueError(f"Unsupported test_type: {test_type}")

def run_simulation(*, test_type: str, dll_path: str, index, material_parameters, num_steps, end_time,
                   maximum_strain, initial_effective_cell_pressure, cohesion_phi_indices=None, axes=None,
                   plotter=None, logger=None, drainage: str | None=None):
    log = logger or (lambda msg, level="info": None)
    tmp_folder = tempfile.mkdtemp(prefix=f"{test_type}_")

    try:
        log(f"Starting {test_type} simulation...", "info")
        json_path, project_path, mdpa_path = setup_simulation_files(test_type, tmp_folder)

        set_material_constitutive_law(json_path, dll_path, material_parameters, index)
        set_project_parameters(project_path, num_steps, end_time, initial_effective_cell_pressure)
        set_mdpa(mdpa_path, maximum_strain, initial_effective_cell_pressure, num_steps, end_time, test_type)

        runner = GenericTestRunner([os.path.join(tmp_folder, 'gid_output', "output.post.res")], tmp_folder)
        tensors, yy_strain, vol_strain, von_mises, mean_stress, shear_xy, shear_strain_xy = runner.run()
        log("Finished analysis; collecting results...", "info")

        sigma_1, sigma_3 = calculate_principal_stresses(tensors)
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
             "phi": friction_angle
        }

        if plotter is None:
            if axes:
                log('Axes were provided but no plotter object was passed. '
                    'The core no longer creates a Matplotlib plotter automatically. '
                    'Please construct a plotter in the UI layer and pass it via `plotter=`.',
                    'warn')
            plotter = _NoOpPlotter()

        _render_with_plotter(test_type, plotter, results)
        log("Rendering complete.", "info")
        return results

    finally:
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)
