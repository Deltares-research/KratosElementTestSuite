import unittest

from kratos_element_test.model.io.lab_results_csv_parser import _parse_float


class LabResultsCsvParserTest(unittest.TestCase):

    def test_parse_float_returns_none_for_blank_values(self):
        self.assertIsNone(_parse_float("", 2, "test_column"))
        self.assertIsNone(_parse_float("   ", 2, "test_column"))

    def test_parse_float_accepts_supported_numeric_formats(self):
        test_cases = [
            ("12,34", 12.34),
            ("12,000.0", 12000.0),
            ("1.23e-4", 1.23e-4),
            ("1,23E-4", 1.23e-4),
            ("+1,23E+4", 1.23e4),
            ("-0,00E+00", -0.0),
            ("1 234,56", 1234.56),
            ("  7 654.321  ", 7654.321),
        ]

        for raw_value, expected in test_cases:
            with self.subTest(raw_value=raw_value):
                self.assertEqual(
                    _parse_float(raw_value, 2, "test_column"),
                    expected,
                )

    def test_parse_float_raises_for_invalid_value(self):
        with self.assertRaises(ValueError) as context:
            _parse_float("abc", 7, "shear_stress")

        self.assertIn("Invalid numeric value 'abc'", str(context.exception))
        self.assertIn("column 'shear_stress'", str(context.exception))
        self.assertIn("line 7", str(context.exception))
