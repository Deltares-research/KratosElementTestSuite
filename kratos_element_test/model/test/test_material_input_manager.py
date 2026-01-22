import unittest

from kratos_element_test.model.material_input_manager import MaterialInputManager


class MaterialInputManagerTest(unittest.TestCase):
    def test_get_and_set_of_current_material_type(self):
        material_input_manager = MaterialInputManager()

        material_input_manager.set_current_material_type("linear_elastic")

        self.assertEqual(
            material_input_manager.get_current_material_type(), "linear_elastic"
        )


if __name__ == "__main__":
    unittest.main()
