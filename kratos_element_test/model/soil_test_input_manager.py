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
        self.input_data = {
            TRIAXIAL: TriaxialAndShearSimulationInputs(
                test_type=TEST_NAME_TO_TYPE.get(TRIAXIAL),
                maximum_strain=20.0,
                initial_effective_cell_pressure=100.0,
                number_of_steps=100,
                duration=1.0,
            ),
            DIRECT_SHEAR: TriaxialAndShearSimulationInputs(
                test_type=TEST_NAME_TO_TYPE.get(TRIAXIAL),
                maximum_strain=20.0,
                initial_effective_cell_pressure=100.0,
                number_of_steps=100,
                duration=1.0,
            ),
            CRS: CRSSimulationInputs(
                test_type=TEST_NAME_TO_TYPE.get(CRS),
                strain_increments=self._create_default_strain_increments(),
            ),
        }

    def _create_default_strain_increments(self):
        return [StrainIncrement(duration=1.0, strain_increment=0.0, steps=100) for _ in range(5)]
