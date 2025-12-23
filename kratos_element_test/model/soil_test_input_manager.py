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
                strain_increments=[self.default_strain_increment() for _ in range(5)],
            ),
        }
        self.update_crs_totals()

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
        print("Updated initial pressure:", new_pressure)

    def update_max_strain(self, new_strain: float, test_type: str) -> None:
        self.input_data[test_type].maximum_strain = new_strain

    def update_num_steps(self, new_steps: int, test_type: str) -> None:
        self.input_data[test_type].number_of_steps = new_steps

    def update_duration(self, new_duration: float, test_type: str) -> None:
        self.input_data[test_type].duration = new_duration

    def add_strain_increment(self):
        crs_inputs = self.input_data.get(CRS)
        crs_inputs.strain_increments.append(self.default_strain_increment())

        self.update_crs_totals()

    def remove_last_crs_strain_increment(self):
        if len(self.input_data[CRS].strain_increments) > 1:
            self.input_data[CRS].strain_increments.pop()

    @staticmethod
    def default_strain_increment():
        return StrainIncrement(duration_in_hours=1.0, strain_increment=0.0, steps=100)
