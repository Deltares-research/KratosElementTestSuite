import csv
import unittest
from unittest.mock import patch

from kratos_element_test.model.io.lab_results_csv_parser import (
    _detect_csv_dialect,
    _parse_float,
)


class LabResultsCsvParserTest(unittest.TestCase):

    def test_detect_csv_dialect_returns_excel_for_empty_sample(self):
        self.assertIs(_detect_csv_dialect("   \n\t  "), csv.excel)

    def test_detect_csv_dialect_detects_semicolon_delimiter(self):
        dialect = _detect_csv_dialect("yy_strain;sigma1;sigma3\n0.0;-100;-100\n")

        self.assertEqual(dialect.delimiter, ";")

    def test_detect_csv_dialect_detects_tab_delimiter(self):
        dialect = _detect_csv_dialect("yy_strain\tsigma1\tsigma3\n0.0\t-100\t-100\n")

        self.assertEqual(dialect.delimiter, "\t")

    def test_detect_csv_dialect_falls_back_to_first_line_counts(self):
        with patch("csv.Sniffer.sniff", side_effect=csv.Error("ambiguous sample")):
            dialect = _detect_csv_dialect("yy_strain|sigma1|sigma3\n0.0|-100|-100\n")

        self.assertEqual(dialect.delimiter, "|")

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
