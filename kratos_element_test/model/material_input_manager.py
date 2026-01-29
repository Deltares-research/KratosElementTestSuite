from kratos_element_test.model.io.udsm_parser import udsm_parser
from kratos_element_test.model.material_inputs import (
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
        self._current_udsm_number = 0

    def set_current_material_type(self, material_type: str) -> None:
        if material_type not in self._material_inputs:
            raise ValueError(f"Invalid material type {material_type}")
        self._current_material_type = material_type
        print(f"Set material type to {material_type}")

    def get_current_material_type(self) -> str:
        return self._current_material_type

    def get_current_material_inputs(
        self,
    ) -> LinearElasticMaterialInputs | MohrCoulombMaterialInputs | UDSMMaterialInputs:
        if (
            self.get_current_material_type() == "udsm"
            and len(self._material_inputs["udsm"]) == 0
        ):
            raise RuntimeError(
                "UDSM material inputs have not been initialized. Please initialize UDSM first."
            )

        return (
            self._material_inputs[self.get_current_material_type()][
                self._current_udsm_number
            ]
            if self.get_current_material_type() == "udsm"
            else self._material_inputs[self.get_current_material_type()]
        )

    def update_material_parameter_of_current_type(self, key, value):
        current_material_inputs = (
            self.get_current_material_inputs().changeable_material_parameters
        )
        if key not in current_material_inputs:
            raise KeyError(
                f"This material parameter ({key}) is not available for the current material type ({self.get_current_material_type()})"
            )

        current_material_inputs[key].value = value
        print(f"Changed {key} to {value}")

    def initialize_udsm(self, dll_path):
        self.set_current_material_type("udsm")
        self._material_inputs["udsm"].clear()
        self._current_udsm_number = 0
        model_dict = udsm_parser(dll_path)
        index = 1
        for parameter_names, parameter_units, model_name in zip(
            model_dict["param_names"],
            model_dict["param_units"],
            model_dict["model_name"],
        ):
            changeableparameters = {}
            for name, unit in zip(parameter_names, parameter_units):
                changeableparameters[name] = Parameter(0.0, unit)
            inputs = UDSMMaterialInputs()
            inputs.material_parameters["UDSM_NAME"] = dll_path
            inputs.material_parameters["UDSM_NUMBER"] = index
            index += 1
            inputs.changeable_material_parameters = changeableparameters
            inputs.model_name = model_name
            self._material_inputs["udsm"].append(inputs)

    def set_current_udsm_number(self, udsm_number):
        self._current_udsm_number = udsm_number

    def get_udsm_model_names(self):
        if len(self._material_inputs["udsm"]) == 0:
            raise RuntimeError(
                "UDSM material inputs have not been initialized. Please initialize UDSM first."
            )
        return [udsm_inputs.model_name for udsm_inputs in self._material_inputs["udsm"]]
