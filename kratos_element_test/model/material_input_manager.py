from kratos_element_test.model.material_inputs import (
    LinearElasticMaterialInputs,
    MohrCoulombMaterialInputs,
    UDSMMaterialInputs,
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

    def get_current_material_type(self) -> str:
        return self._current_material_type

    def get_current_material_inputs(self):
        return self._material_inputs[self.get_current_material_type()]

    def update_material_parameter_of_current_type(self, key, value):
        current_material_inputs = self._material_inputs[
            self.get_current_material_type()
        ].changeable_material_parameters
        if key not in current_material_inputs:
            raise KeyError(
                f"This material parameter ({key}) is not available for the current material type ({self.get_current_material_type()})"
            )

        current_material_inputs[key] = value
