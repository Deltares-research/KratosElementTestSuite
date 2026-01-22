from kratos_element_test.model.material_inputs import LinearElasticMaterialInputs


class MaterialInputManager:
    def __init__(self):
        self._current_material_type = ""
        self._material_inputs = {"linear_elastic": LinearElasticMaterialInputs()}

    def set_current_material_type(self, material_type: str) -> None:
        self._current_material_type = material_type

    def get_current_material_type(self) -> str:
        return self._current_material_type

    def get_current_material_inputs(self):
        return self._material_inputs[self.get_current_material_type()]
