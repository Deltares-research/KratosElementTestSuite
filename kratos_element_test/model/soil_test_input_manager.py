from kratos_element_test.model.models import (
    TriaxialAndShearSimulationInputs,
    CRSSimulationInputs,
    StrainIncrement,
)
from kratos_element_test.view.ui_constants import (
    TRIAXIAL,
    DIRECT_SHEAR,
    TEST_NAME_TO_TYPE,
    CRS,
)


class SoilTestInputManager:
    def __init__(self):
        self.input_data = {}
        self.input_data[TRIAXIAL] = TriaxialAndShearSimulationInputs(
            test_type=TEST_NAME_TO_TYPE.get(TRIAXIAL),
            maximum_strain=20.0,
            initial_effective_cell_pressure=100.0,
            number_of_steps=100,
            duration=1.0,
        )

        self.input_data[DIRECT_SHEAR] = TriaxialAndShearSimulationInputs(
            test_type=TEST_NAME_TO_TYPE.get(TRIAXIAL),
            maximum_strain=20.0,
            initial_effective_cell_pressure=100.0,
            number_of_steps=100,
            duration=1.0,
        )

        default_strain_increments = []
        for i in range(5):
            default_strain_increments.append(
                StrainIncrement(duration=1.0, strain_increment=0.0, steps=100)
            )
        self.input_data[CRS] = CRSSimulationInputs(
            test_type=TEST_NAME_TO_TYPE.get(CRS),
            strain_increments=default_strain_increments,
        )
