import unittest

from kratos_element_test.model.material_input_manager import MaterialInputManager
from kratos_element_test.model.material_inputs import LinearElasticMaterialInputs


class MaterialInputManagerTest(unittest.TestCase):
    def test_get_and_set_of_current_material_type(self):
        material_input_manager = MaterialInputManager()

        material_input_manager.set_current_material_type("linear_elastic")

        self.assertEqual(
            material_input_manager.get_current_material_type(), "linear_elastic"
        )

    def test_default_input_for_linear_elastic_material(self):
        material_input_manager = MaterialInputManager()
        material_input_manager.set_current_material_type("linear_elastic")

        linear_elastic_material_inputs = (
            material_input_manager.get_current_material_inputs()
        )

        self.assertEqual(linear_elastic_material_inputs, LinearElasticMaterialInputs())

    def test_changing_linear_elastic_material_inputs(self):
        material_input_manager = MaterialInputManager()
        material_input_manager.set_current_material_type("linear_elastic")

        material_input_manager.update_material_parameter_of_current_type(
            "YOUNG_MODULUS", 9e5
        )

        linear_elastic_material_inputs = (
            material_input_manager.get_current_material_inputs()
        )

        self.assertEqual(
            linear_elastic_material_inputs.material_parameters["YOUNG_MODULUS"], 9e5
        )

    def tests_changing_nonexisting_material_inputs_throws(self):
        material_input_manager = MaterialInputManager()
        material_input_manager.set_current_material_type("linear_elastic")
        material_input_manager.update_material_parameter_of_current_type(
            "NONEXISTING", 9e5
        )
        self.assertRaises(
            ValueError,
            lambda: material_input_manager.update_material_parameter_of_current_type(
                "NONEXISTING", 9e5
            ),
        )


if __name__ == "__main__":
    unittest.main()
