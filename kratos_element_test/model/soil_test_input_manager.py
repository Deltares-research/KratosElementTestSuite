from kratos_element_test.model.core_utils import hours_to_seconds
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
        self.update_crs_totals()

    def _create_default_strain_increments(self):
        return [StrainIncrement(duration_in_hours=1.0, strain_increment=0.0, steps=100) for _ in range(5)]

    def update_crs_totals(self):
        crs_inputs = self.input_data.get(CRS)
        crs_inputs.number_of_steps = sum(
            increment.steps for increment in crs_inputs.strain_increments
        )
        crs_inputs.duration_in_seconds = hours_to_seconds(sum(
            increment.duration_in_hours for increment in crs_inputs.strain_increments
        ))
        crs_inputs.maximum_strain = sum(
            increment.strain_increment for increment in crs_inputs.strain_increments
        )

    def set_crs_strain_increment(self, index, new_increment):
        crs_inputs = self.input_data.get(CRS)
        crs_inputs.strain_increments[index].strain_increment = new_increment

        self.update_crs_totals()

    def set_crs_duration(self, index, new_duration_in_hours):
        crs_inputs = self.input_data.get(CRS)
        crs_inputs.strain_increments[index].duration_in_hours = new_duration_in_hours

        self.update_crs_totals()

    def set_crs_steps(self, index, new_steps):
        crs_inputs = self.input_data.get(CRS)
        crs_inputs.strain_increments[index].steps = new_steps

        self.update_crs_totals()
