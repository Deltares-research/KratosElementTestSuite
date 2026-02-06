from pathlib import Path

from kratos_element_test.model.io.udsm_parser import udsm_parser
from kratos_element_test.model.material_input_data_models import (
    LinearElasticMaterialInputs,
    MohrCoulombMaterialInputs,
    UDSMMaterialInputs,
    Parameter,
)


class MaterialInputManager:
    def __init__(self):
        self._current_material_type = ""
        self._material_inputs = {
            "linear_elastic": LinearElasticMaterialInputs(),
            "mohr_coulomb": MohrCoulombMaterialInputs(),
            "udsm": [],
        }
        self._current_udsm_index = 0

    def set_current_material_type(self, material_type: str) -> None:
        if material_type not in self._material_inputs:
            raise ValueError(f"Invalid material type {material_type}")
        self._current_material_type = material_type

    def get_current_material_type(self) -> str:
        return self._current_material_type

    def get_current_material_inputs(
        self,
    ) -> LinearElasticMaterialInputs | MohrCoulombMaterialInputs | UDSMMaterialInputs:
        if self.get_current_material_type() == "udsm":
            assert (
                len(self._material_inputs["udsm"]) > 0
            ), "UDSM material inputs have not been initialized. Please initialize UDSM first."

        material_input = self._material_inputs[self.get_current_material_type()]
        return (
            material_input[self._current_udsm_index]
            if self.get_current_material_type() == "udsm"
            else material_input
        )

    def update_material_parameter_of_current_type(self, key, value):
        current_material_inputs = (
            self.get_current_material_inputs().user_defined_parameters
        )
        if key not in current_material_inputs:
            raise KeyError(
                f"This material parameter ({key}) is not available for the current material type ({self.get_current_material_type()})"
            )

        current_material_inputs[key].value = value

    def initialize_udsm(self, dll_path: Path):
        self.set_current_material_type("udsm")
        self._material_inputs["udsm"].clear()
        self._current_udsm_index = 0
        model_dict = udsm_parser(str(dll_path.resolve()))
        udsm_number = 1
        for index, (parameter_names, parameter_units, model_name) in enumerate(
            zip(
                model_dict["param_names"],
                model_dict["param_units"],
                model_dict["model_name"],
            )
        ):
            user_defined_parameters = {}
            for name, unit in zip(parameter_names, parameter_units):
                user_defined_parameters[name] = Parameter(0.0, unit)
            inputs = UDSMMaterialInputs()
            inputs.material_parameters["UDSM_NAME"] = str(dll_path.resolve())
            inputs.material_parameters["UDSM_NUMBER"] = index + 1
            udsm_number += 1
            inputs.user_defined_parameters = user_defined_parameters
            inputs.model_name = model_name
            self._material_inputs["udsm"].append(inputs)

    def get_udsm_model_names(self):
        assert (
            len(self._material_inputs["udsm"]) > 0
        ), "UDSM material inputs have not been initialized. Please initialize UDSM first."
        return [udsm_inputs.model_name for udsm_inputs in self._material_inputs["udsm"]]

    def set_current_udsm_model(self, model_name):
        self._current_udsm_index = self.get_udsm_model_names().index(model_name)

    def set_mohr_enabled(self, enabled):
        assert self.get_current_material_type() == "udsm"
        material_inputs = self.get_current_material_inputs()
        material_inputs.mohr_coulomb_options.enabled = enabled

    def get_mohr_enabled(self):
        assert self.get_current_material_type() == "udsm"
        material_inputs = self.get_current_material_inputs()
        return material_inputs.mohr_coulomb_options.enabled

    def set_cohesion_index(self, cohesion_index):
        assert self.get_current_material_type() == "udsm"
        material_inputs = self.get_current_material_inputs()
        material_inputs.mohr_coulomb_options.c_index = cohesion_index

    def set_phi_index(self, phi_index):
        assert self.get_current_material_type() == "udsm"
        material_inputs = self.get_current_material_inputs()
        material_inputs.mohr_coulomb_options.phi_index = phi_index
