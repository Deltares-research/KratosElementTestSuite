# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict


@dataclass
class MohrCoulombOptions:
    enabled: bool = False
    c_index: Optional[int] = None  # 1-based index from the UDSM mapping
    phi_index: Optional[int] = None

    def to_indices(self) -> Optional[Tuple[int, int]]:
        if not self.enabled or self.c_index is None or self.phi_index is None:
            return None
        return self.c_index, self.phi_index


@dataclass
class LinearElasticMaterialInputs:
    kratos_law_name: str = "GeoLinearElasticPlaneStrain2DLaw"
    material_parameters: Dict = field(
        default_factory=lambda: {
            "YOUNG_MODULUS": 0.0,
            "POISSON_RATIO": 0.0,
        }
    )
