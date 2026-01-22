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
class Parameter:
    value: float | str = 0.0
    unit: str = "-"

@dataclass
class LinearElasticMaterialInputs:
    kratos_law_name: str = "GeoLinearElasticPlaneStrain2DLaw"
    changeable_material_parameters: Dict = field(
        default_factory=lambda: {
            "YOUNG_MODULUS": 0.0,
            "POISSON_RATIO": 0.0,
        }
    )

    def get_kratos_inputs(self) -> Dict:
        return self.changeable_material_parameters

@dataclass
class MohrCoulombMaterialInputs:
    kratos_law_name: str = "GeoMohrCoulombWithTensionCutOff2D"
    changeable_material_parameters: Dict = field(
        default_factory=lambda: {
            "YOUNG_MODULUS": 0.0,
            "POISSON_RATIO": 0.0,
            "GEO_COHESION": 0.0,
            "GEO_FRICTION_ANGLE": 0.0,
            "GEO_TENSILE_STRENGTH": 0.0,
            "GEO_DILATANCY_ANGLE": 0.0,
        }
    )
    mohr_coulomb_options: MohrCoulombOptions = field(
        default_factory=lambda: MohrCoulombOptions(enabled=True, c_index=3, phi_index=4)
    )

    def get_kratos_inputs(self) -> Dict:
        return self.changeable_material_parameters


@dataclass
class UDSMMaterialInputs:
    kratos_law_name: str = "SmallStrainUDSM2DPlaneStrainLaw"
    changeable_material_parameters = Dict
    material_parameters: Dict = field(
        default_factory=lambda: {
            "IS_FORTRAN_UDSM": True,
            "UMAT_PARAMETERS": [],
            "UDSM_NAME": "",
            "UDSM_NUMBER": 0,
        }
    )
    mohr_coulomb_options: MohrCoulombOptions | None = None

    def get_kratos_inputs(self) -> Dict:
        result = self.material_parameters
        result["UMAT_PARAMETERS"] = self.changeable_material_parameters.values()
        return result
