from kratos_element_test.model.soil_test_input_manager import SoilTestInputManager


class MainModel:
    def __init__(self):
        self.soil_test_input_manager = SoilTestInputManager()

    def get_current_test_type(self) -> str:
        return self.soil_test_input_manager.get_current_test_type()
