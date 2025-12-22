from kratos_element_test.model.models import SimulationInputs, TriaxialSimulationInputs
from kratos_element_test.view.ui_constants import (
    CRS,
    TRIAXIAL,
    DIRECT_SHEAR,
    TEST_NAME_TO_TYPE,
)


class SoilTestInputManager:
    def __init__(self):
        self.input_data = {}
        self.input_data[TRIAXIAL] = TriaxialSimulationInputs(test_type=TEST_NAME_TO_TYPE.get(TRIAXIAL), maximum_strain=20.0,
                                                     initial_effective_cell_pressure=100.0,
                                                     number_of_steps=100,
                                                     duration=1.0)




