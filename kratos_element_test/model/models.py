# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

from dataclasses import dataclass, field
from kratos_element_test.view.ui_constants import VALID_TEST_TYPES


@dataclass
class TriaxialAndShearSimulationInputs:
    test_type: VALID_TEST_TYPES
    maximum_strain: float = 20.0
    initial_effective_cell_pressure: float = 100.0
    number_of_steps: int = 100
    duration_in_seconds: float = 1.0
    drainage: str = "drained"

    def validate(self) -> None:
        if self.test_type not in ("triaxial", "direct_shear"):
            raise ValueError(f"Unsupported test type: {self.test_type}.")
        if self.number_of_steps <= 0:
            raise ValueError(
                f"Number of steps must be > 0, but got {self.number_of_steps}."
            )
        if self.duration_in_seconds <= 0:
            raise ValueError(
                f"Duration must be > 0, but got {self.duration_in_seconds}."
            )
        if self.drainage not in ("drained", "undrained"):
            raise ValueError(f"Unsupported drainage type: {self.drainage}.")


@dataclass
class StrainIncrement:
    duration_in_hours: float = 1.0
    strain_increment: float = 0.0
    steps: int = 100

    def validate(self) -> None:
        if abs(self.strain_increment) >= 100.0:
            raise ValueError(
                f"Strain increment must be between -100.0% and 100.0%, but got {self.strain_increment}"
            )
        if self.steps <= 0:
            raise ValueError(f"Number of steps must be > 0, but got {self.steps}")
        if self.duration_in_hours <= 0:
            raise ValueError(f"Duration must be > 0, but got {self.duration_in_hours}")


@dataclass
class CRSSimulationInputs:
    test_type: VALID_TEST_TYPES
    strain_increments: list[StrainIncrement] = field(
        default_factory=lambda: [StrainIncrement() for _ in range(5)]
    )
    maximum_strain: float = 0.0
    number_of_steps: int = 0
    duration_in_seconds: float = 0.0
    initial_effective_cell_pressure: float = 0.0

    def validate(self) -> None:
        if self.test_type not in VALID_TEST_TYPES:
            raise ValueError(f"Unsupported test type: {self.test_type}.")
        for strain_increment in self.strain_increments:
            strain_increment.validate()
