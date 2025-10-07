# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

from dataclasses import dataclass, field
from typing import Optional, Tuple
from kratos_element_test.ui.ui_constants import VALID_TEST_TYPES, VALID_DRAINAGE_TYPES


@dataclass
class MohrCoulombOptions:
    enabled: bool = False
    c_index: Optional[int] = None   # 1-based index from the UDSM mapping
    phi_index: Optional[int] = None

    def to_indices(self) -> Optional[Tuple[int, int]]:
        if not self.enabled or self.c_index is None or self.phi_index is None:
            return None
        return self.c_index, self.phi_index


@dataclass
class SimulationInputs:
    test_type: VALID_TEST_TYPES
    maximum_strain: float
    initial_effective_cell_pressure: float
    stress_increment: float
    number_of_steps: int
    duration: float
    drainage: VALID_DRAINAGE_TYPES = "drained"
    mohr_coulomb: MohrCoulombOptions = field(default_factory=MohrCoulombOptions)

    def validate(self) -> None:
        if self.test_type not in ("triaxial", "direct_shear", "crs"):
            raise ValueError("Unsupported test type.")
        if self.number_of_steps <= 0:
            raise ValueError("Number of steps must be > 0.")
        if self.duration <= 0:
            raise ValueError("Duration must be > 0.")
