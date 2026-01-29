from typing import Any

from kratos_element_test.model.material_input_data_models import (
    MohrCoulombMaterialInputs,
    LinearElasticMaterialInputs,
    UDSMMaterialInputs,
)


def get_cohesion_and_phi(
    material_inputs: (
        LinearElasticMaterialInputs | MohrCoulombMaterialInputs | UDSMMaterialInputs
    ),
) -> tuple[None, None] | tuple[float, float]:
    if isinstance(material_inputs, UDSMMaterialInputs) or isinstance(
        material_inputs, MohrCoulombMaterialInputs
    ):
        material_parameters = [
            parameter.value
            for parameter in material_inputs.changeable_material_parameters.values()
        ]
        return (
            material_parameters[material_inputs.mohr_coulomb_options.c_index - 1],
            material_parameters[material_inputs.mohr_coulomb_options.phi_index - 1],
        )
    return None, None
