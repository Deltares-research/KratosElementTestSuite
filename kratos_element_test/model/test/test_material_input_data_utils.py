import unittest

from kratos_element_test.model.material_input_data_models import (
    MohrCoulombMaterialInputs,
    UDSMMaterialInputs,
    Parameter,
    LinearElasticMaterialInputs,
)
from kratos_element_test.model.material_input_data_utils import get_cohesion_and_phi


class MaterialInputUtilsTest(unittest.TestCase):
    def test_get_c_and_phi_from_mohr_coulomb_model(self):
        mohr_coulomb_inputs = MohrCoulombMaterialInputs()
        mohr_coulomb_inputs.user_defined_parameters["GEO_COHESION"].value = 1.0
        mohr_coulomb_inputs.user_defined_parameters[
            "GEO_FRICTION_ANGLE"
        ].value = 25.0

        c, phi = get_cohesion_and_phi(mohr_coulomb_inputs)

        self.assertEqual(c, 1.0)
        self.assertEqual(phi, 25.0)

    def test_get_c_and_phi_from_udsm_model(self):
        udsm_inputs = UDSMMaterialInputs()
        user_defined_parameters = {
            "Param1": Parameter(value=1.0),
            "Param2": Parameter(value=2.0),
            "Param3": Parameter(value=3.0),
            "Param4": Parameter(value=4.0),
        }
        udsm_inputs.user_defined_parameters = user_defined_parameters
        udsm_inputs.mohr_coulomb_options.enabled = True
        udsm_inputs.mohr_coulomb_options.c_index = 2
        udsm_inputs.mohr_coulomb_options.phi_index = 3

        c, phi = get_cohesion_and_phi(udsm_inputs)

        self.assertEqual(c, 2.0)
        self.assertEqual(phi, 3.0)

    def test_get_c_and_phi_from_udsm_model_returns_none_if_mc_disabled(self):
        udsm_inputs = UDSMMaterialInputs()
        user_defined_parameters = {
            "Param1": Parameter(value=1.0),
            "Param2": Parameter(value=2.0),
            "Param3": Parameter(value=3.0),
            "Param4": Parameter(value=4.0),
        }
        udsm_inputs.user_defined_parameters = user_defined_parameters
        udsm_inputs.mohr_coulomb_options.enabled = False
        udsm_inputs.mohr_coulomb_options.c_index = 2
        udsm_inputs.mohr_coulomb_options.phi_index = 3

        c, phi = get_cohesion_and_phi(udsm_inputs)

        self.assertIsNone(c)
        self.assertIsNone(phi)

    def test_get_c_and_phi_from_linear_elastic_model(self):
        linear_elastic_inputs = LinearElasticMaterialInputs()

        c, phi = get_cohesion_and_phi(linear_elastic_inputs)

        self.assertIsNone(c)
        self.assertIsNone(phi)


if __name__ == "__main__":
    unittest.main()
