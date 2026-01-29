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
            "udsm": UDSMMaterialInputs(),
        }

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
        return self._material_inputs[self.get_current_material_type()]

    def update_material_parameter_of_current_type(self, key, value):
        current_material_inputs = self._material_inputs[
            self.get_current_material_type()
        ].changeable_material_parameters
        if key not in current_material_inputs:
            raise KeyError(
                f"This material parameter ({key}) is not available for the current material type ({self.get_current_material_type()})"
            )

        current_material_inputs[key].value = value
        print(f"Changed {key} to {value}")

    def initialize_udsm(self, dll_path):
        self.set_current_material_type("udsm")
        model_dict = udsm_parser(dll_path)
        print(model_dict)
        names_of_first_model = model_dict["param_names"][0]
        parameters_of_first_model = model_dict["param_units"][0]
        changeableparameters = {}
        for name, unit in zip(names_of_first_model, parameters_of_first_model):
            changeableparameters[name] = Parameter(0.0, unit)

        self.get_current_material_inputs().changeable_material_parameters = (
            changeableparameters
        )
        self.get_current_material_inputs().material_parameters["UDSM_NAME"] = dll_path
