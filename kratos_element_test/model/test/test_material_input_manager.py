import unittest
from pathlib import Path

from parameterized import parameterized

from kratos_element_test.model.material_input_manager import MaterialInputManager
from kratos_element_test.model.material_input_data_models import (
    LinearElasticMaterialInputs,
    MohrCoulombMaterialInputs,
    UDSMMaterialInputs,
    Parameter,
)
from kratos_element_test.view.ui_utils import asset_path, soil_models_dir


class MaterialInputManagerTest(unittest.TestCase):
    def test_get_and_set_of_current_material_type(self):
        material_input_manager = MaterialInputManager()

        material_input_manager.set_current_material_type("linear_elastic")

        self.assertEqual(
            material_input_manager.get_current_material_type(), "linear_elastic"
        )

    @parameterized.expand(
        [
            ["linear_elastic", LinearElasticMaterialInputs()],
            ["mohr_coulomb", MohrCoulombMaterialInputs()],
        ]
    )
    def test_default_input_for_materials(self, name, expected_defaults):
        material_input_manager = MaterialInputManager()
        material_input_manager.set_current_material_type(name)

        material_inputs = material_input_manager.get_current_material_inputs()

        self.assertEqual(material_inputs, expected_defaults)

    def test_getting_udsm_material_inputs_without_initializing_udsm_throws(self):
        material_input_manager = MaterialInputManager()
        material_input_manager.set_current_material_type("udsm")

        self.assertRaises(
            RuntimeError, material_input_manager.get_current_material_inputs
        )

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
            linear_elastic_material_inputs.get_kratos_inputs()["YOUNG_MODULUS"],
            9e5,
        )

    def tests_changing_nonexisting_material_inputs_throws(self):
        material_input_manager = MaterialInputManager()
        material_input_manager.set_current_material_type("linear_elastic")
        self.assertRaises(
            KeyError,
            lambda: material_input_manager.update_material_parameter_of_current_type(
                "NONEXISTING", 9e5
            ),
        )

    def test_setting_nonexistent_material_type_throws(self):
        material_input_manager = MaterialInputManager()
        self.assertRaises(
            ValueError,
            lambda: material_input_manager.set_current_material_type("nonexistent"),
        )

    def test_loading_udsm_initializes_material_inputs(self):
        material_input_manager = MaterialInputManager()
        material_input_manager.initialize_udsm(
            Path(soil_models_dir()) / "sclay1creep.dll"
        )

        material_input_manager.set_current_material_type("udsm")

        udsm_material_inputs = material_input_manager.get_current_material_inputs()

        self.assertIsInstance(udsm_material_inputs, UDSMMaterialInputs)
        self.assertEqual(udsm_material_inputs.model_name, "Deltares-SClay1S")
        self.assertEqual(udsm_material_inputs.material_parameters["UDSM_NUMBER"], 1)

        expected_changeable_material_parameters = {
            "k": Parameter(value=0.0, unit="-"),
            "l": Parameter(value=0.0, unit="-"),
            "m": Parameter(value=0.0, unit="-"),
            "n": Parameter(value=0.0, unit="-"),
            "fₜ𝒸": Parameter(value=0.0, unit="Degrees"),
            "r": Parameter(value=0.0, unit="-"),
            "w": Parameter(value=0.0, unit="-"),
            "w𝒹": Parameter(value=0.0, unit="-"),
            "t": Parameter(value=0.0, unit="days"),
            "a₀": Parameter(value=0.0, unit="-"),
            "OCR": Parameter(value=0.0, unit="-"),
            "e₀": Parameter(value=0.0, unit="-"),
        }

        self.assertEqual(
            udsm_material_inputs.changeable_material_parameters,
            expected_changeable_material_parameters,
        )
        self.assertEqual(
            udsm_material_inputs.get_kratos_inputs()["UMAT_PARAMETERS"],
            [0.0] * len(expected_changeable_material_parameters),
        )

        material_input_manager.set_current_udsm_number(1)

        udsm_material_inputs = material_input_manager.get_current_material_inputs()
        self.assertIsInstance(udsm_material_inputs, UDSMMaterialInputs)
        self.assertEqual(udsm_material_inputs.model_name, "Deltares-SClay1S-Fibres")
        self.assertEqual(udsm_material_inputs.material_parameters["UDSM_NUMBER"], 2)

        expected_changeable_material_parameters = {
            "k": Parameter(value=0.0, unit="-"),
            "l": Parameter(value=0.0, unit="-"),
            "m": Parameter(value=0.0, unit="-"),
            "n": Parameter(value=0.0, unit="-"),
            "fₜ𝒸": Parameter(value=0.0, unit="Degrees"),
            "r": Parameter(value=0.0, unit="-"),
            "w": Parameter(value=0.0, unit="-"),
            "w𝒹": Parameter(value=0.0, unit="-"),
            "t": Parameter(value=0.0, unit="days"),
            "a₀": Parameter(value=0.0, unit="-"),
            "OCR": Parameter(value=0.0, unit="-"),
            "e₀": Parameter(value=0.0, unit="-"),
            "Efib": Parameter(value=0.0, unit="kN/m"),
            "sₜₑₙ": Parameter(value=0.0, unit="kN/m"),
            "s𝒸ₒₘ": Parameter(value=0.0, unit="kN/m"),
            "a": Parameter(value=0.0, unit="[Degrees]"),
        }

        self.assertEqual(
            udsm_material_inputs.changeable_material_parameters,
            expected_changeable_material_parameters,
        )
        self.assertEqual(
            udsm_material_inputs.get_kratos_inputs()["UMAT_PARAMETERS"],
            [0.0] * len(expected_changeable_material_parameters),
        )

    def test_getting_udsm_model_names(self):
        material_input_manager = MaterialInputManager()
        material_input_manager.initialize_udsm(
            Path(soil_models_dir()) / "sclay1creep.dll"
        )

        self.assertEqual(
            material_input_manager.get_udsm_model_names(),
            ["Deltares-SClay1S", "Deltares-SClay1S-Fibres"],
        )


if __name__ == "__main__":
    unittest.main()
