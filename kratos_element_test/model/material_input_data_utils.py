from kratos_element_test.model.material_input_data_models import (
    MohrCoulombMaterialInputs,
    LinearElasticMaterialInputs,
    UDSMMaterialInputs,
)

from typing import Dict


def get_cohesion_and_phi(
    material_inputs: (
        LinearElasticMaterialInputs | MohrCoulombMaterialInputs | UDSMMaterialInputs
    ),
) -> tuple[None, None] | tuple[float, float]:
    try:
        return material_inputs.get_cohesion_and_phi()
    except AttributeError:
        return None, None


def convert_user_inputs_to_kratos_inputs(
    user_defined_parameters: Dict[str, float],
) -> Dict[str, float]:
    result = {}
    for key, value in user_defined_parameters.items():
        result[key] = value.value
    return result
