class MaterialInputManager:
    def __init__(self):
        self._current_material_type = ""

    def set_current_material_type(self, material_type: str) -> None:
        self._current_material_type = material_type

    def get_current_material_type(self) -> str:
        return self._current_material_type
