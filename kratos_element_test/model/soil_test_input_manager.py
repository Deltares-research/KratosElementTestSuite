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
                test_type=TEST_NAME_TO_TYPE.get(TRIAXIAL)
            ),
            DIRECT_SHEAR: TriaxialAndShearSimulationInputs(
                test_type=TEST_NAME_TO_TYPE.get(DIRECT_SHEAR)
            ),
            CRS: CRSSimulationInputs(test_type=TEST_NAME_TO_TYPE.get(CRS)),
        }
        self.update_crs_totals()
        self._current_test_type = TRIAXIAL

    def update_crs_totals(self):
        crs_inputs = self.input_data.get(CRS)
        crs_inputs.number_of_steps = sum(
            increment.steps for increment in crs_inputs.strain_increments
        )
        crs_inputs.duration_in_seconds = hours_to_seconds(
            sum(
                increment.duration_in_hours
                for increment in crs_inputs.strain_increments
            )
        )
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

    def update_init_pressure(self, new_pressure: float, test_type: str) -> None:
        self.input_data[test_type].initial_effective_cell_pressure = new_pressure

    def update_max_strain(self, new_strain: float, test_type: str) -> None:
        self.input_data[test_type].maximum_strain = new_strain

    def update_num_steps(self, new_steps: int, test_type: str) -> None:
        self.input_data[test_type].number_of_steps = new_steps

    def update_duration(self, new_duration_in_seconds: float, test_type: str) -> None:
        self.input_data[test_type].duration_in_seconds = new_duration_in_seconds

    def update_drainage(self, new_drainage: str) -> None:
        inputs = self.get_current_test_inputs()
        if hasattr(inputs, "drainage"):
            inputs.drainage = new_drainage

    def add_strain_increment(self):
        crs_inputs = self.input_data.get(CRS)
        crs_inputs.strain_increments.append(StrainIncrement())

        self.update_crs_totals()

    def remove_last_crs_strain_increment(self):
        if len(self.input_data[CRS].strain_increments) > 1:
            self.input_data[CRS].strain_increments.pop()

    def get_current_test_type(self) -> str:
        return self._current_test_type

    def set_current_test_type(self, test_type: str) -> None:
        if test_type not in [TRIAXIAL, DIRECT_SHEAR, CRS]:
            raise ValueError(f"Trying to set a non-existent test type {test_type}")
        self._current_test_type = test_type

    def get_current_test_inputs(
        self,
    ) -> TriaxialAndShearSimulationInputs | CRSSimulationInputs:
        return self.input_data[self._current_test_type]
