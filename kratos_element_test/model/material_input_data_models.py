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
            "YOUNG_MODULUS": Parameter(value=0.0, unit="kN/m²"),
            "POISSON_RATIO": Parameter(value=0.0, unit="-"),
        }
    )

    def get_kratos_inputs(self) -> Dict:
        result = {}
        for name, parameter in self.changeable_material_parameters.items():
            result[name] = parameter.value
        return result


@dataclass
class MohrCoulombMaterialInputs:
    kratos_law_name: str = "GeoMohrCoulombWithTensionCutOff2D"
    changeable_material_parameters: Dict = field(
        default_factory=lambda: {
            "YOUNG_MODULUS": Parameter(value=0.0, unit="kN/m²"),
            "POISSON_RATIO": Parameter(value=0.0, unit="-"),
            "GEO_COHESION": Parameter(value=0.0, unit="kN/m²"),
            "GEO_FRICTION_ANGLE": Parameter(value=0.0, unit="deg"),
            "GEO_TENSILE_STRENGTH": Parameter(value=0.0, unit="kN/m²"),
            "GEO_DILATANCY_ANGLE": Parameter(value=0.0, unit="deg"),
        }
    )
    mohr_coulomb_options: MohrCoulombOptions = field(
        default_factory=lambda: MohrCoulombOptions(enabled=True, c_index=3, phi_index=4)
    )

    def get_kratos_inputs(self) -> Dict:
        result = {}
        for name, parameter in self.changeable_material_parameters.items():
            result[name] = parameter.value
        return result


@dataclass
class UDSMMaterialInputs:
    kratos_law_name: str = "SmallStrainUDSM2DPlaneStrainLaw"
    model_name: str = ""
    changeable_material_parameters = Dict
    material_parameters: Dict = field(
        default_factory=lambda: {
            "IS_FORTRAN_UDSM": True,
            "UMAT_PARAMETERS": [],
            "UDSM_NAME": "",
            "UDSM_NUMBER": 1,
        }
    )
    mohr_coulomb_options: MohrCoulombOptions = field(
        default_factory=lambda: MohrCoulombOptions(
            enabled=False, c_index=None, phi_index=None
        )
    )

    def get_kratos_inputs(self) -> Dict:
        result = self.material_parameters
        result["UMAT_PARAMETERS"] = [
            parameter.value
            for parameter in self.changeable_material_parameters.values()
        ]
        return result
