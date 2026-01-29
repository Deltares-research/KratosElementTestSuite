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
    try:
        return material_inputs.get_cohesion_and_phi()
    except AttributeError:
        return None, None

