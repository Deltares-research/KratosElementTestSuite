import csv
import io
from pathlib import Path
from typing import Dict, List, Optional, Any

from kratos_element_test.view.ui_constants import TEST_NAME_TO_TYPE, VALID_TEST_TYPES

_SYMBOL_REPLACEMENTS = {
    "σ": "sigma",
    "ε": "epsilon",
    "τ": "tau",
    "γ": "gamma",
    "Δ": "delta",
    "ϕ": "phi",
    "ψ": "psi",
    "₁": "1",
    "₂": "2",
    "₃": "3",
    "ₓ": "x",
    "ᵧ": "y",
    "ᵥ": "v",
    "′": "prime",
    "’": "prime",
    "'": "prime",
}


def _normalize_token(value: str) -> str:
    text = str(value).lower().strip()
    for source, target in _SYMBOL_REPLACEMENTS.items():
        text = text.replace(source, target)
    return "".join(ch for ch in text if ch.isalnum())


def _build_alias_map(
    raw_aliases: Dict[str, tuple[str, ...]],
) -> Dict[str, str]:
    alias_map: Dict[str, str] = {}
    for canonical_key, aliases in raw_aliases.items():
        for alias in aliases:
            alias_map[_normalize_token(alias)] = canonical_key
    return alias_map


_RAW_COLUMN_ALIASES = {
    "Vertical Strain": (
        "yy_strain",
        "vertical_strain",
        "vertical strain",
        "axial_strain",
        "axial strain",
        "strain_yy",
        "epsilon_yy",
        "eps_yy",
        "eyy",
        "strain",
        "vertical strain eyy",
    ),
    "Volumetric Strain": (
        "vol_strain",
        "volumetric_strain",
        "volumetric strain",
        "volumetric",
        "strain_v",
        "epsilon_v",
        "eps_v",
        "ev",
        "volumetric strain ev",
    ),
    "sigma_1": (
        "sigma_1",
        "sigma1",
        "s1",
        "principal_stress_1",
        "major_principal_stress",
        "axial_stress",
        "first_principal_stress",
        "first principal stress",
        "major principal stress",
    ),
    "sigma_3": (
        "sigma_3",
        "sigma3",
        "s3",
        "principal_stress_3",
        "minor_principal_stress",
        "confining_stress",
        "confining_pressure",
        "cell_pressure",
        "third_principal_stress",
        "third principal stress",
        "minor principal stress",
    ),
    "sigma1_sigma3_diff": (
        "sigma1_sigma3_diff",
        "delta_sigma",
        "deltasigma",
        "sigma1_minus_sigma3",
        "q_diff",
        "deviator_sigma",
    ),
    "Mean Effective Stress": (
        "Mean Effective Stress",
        "p'",
        "pprime",
        "p_prime",
        "mean_stress",
        "meanstress",
        "mean_effective_stress",
        "mean effective stress",
        "mean_effective_pressure",
        "effective_stress_mean",
        "effective_mean_stress",
        "p_eff",
    ),
    "Deviatoric Stress": (
        "Deviatoric Stress",
        "q",
        "q_stress",
        "deviator_stress",
        "von_mises",
        "deviatoric_stress",
        "deviatoricstress",
        "deviatoric stress",
    ),
    "Tensor Shear Strain": (
        "Tensor Shear Strain",
        "shear_strain_xy",
        "strain_xy",
        "gamma_xy",
        "epsilon_xy",
        "exy",
    ),
    "Shear Stress": (
        "Shear Stress",
        "shear_stress_xy",
        "shear_xy",
        "tau_xy",
        "shear_stress",
    ),
    "sigma_yy": (
        "sigma_yy",
        "sigmayy",
        "sigma_prime_yy",
        "vertical_effective_stress",
        "vertical_stress",
        "effective_vertical_stress",
        "effective vertical stress",
        "vertical effective stress",
    ),
    "sigma_xx": (
        "sigma_xx",
        "sigmaxx",
        "sigma_prime_xx",
        "horizontal_effective_stress",
        "horizontal_stress",
        "effective_horizontal_stress",
        "horizontal effective stress",
    ),
    "time_steps": (
        "time_steps",
        "time",
        "time_h",
        "time_hours",
        "time_hour",
        "hours",
    ),
}

_EXPECTED_COLUMNS_BY_TEST: Dict[str, List[str]] = {
    "triaxial": [
        "yy_strain",
        "sigma1_sigma3_diff",
        "vol_strain",
        "sigma_3",
        "sigma_1",
        "Mean Effective Stress",
        "Deviatoric Stress",
    ],
    "direct_shear": [
        "Tensor Shear Strain",
        "Shear Stress",
        "sigma_3",
        "sigma_1",
        "Mean Effective Stress",
        "Deviatoric Stress",
    ],
    "crs": [
        "yy_strain",
        "sigma_yy",
        "sigma_xx",
        "sigma_3",
        "sigma_1",
        "Mean Effective Stress",
        "Deviatoric Stress",
        "time_steps",
    ],
}

_COLUMN_ALIASES = _build_alias_map(_RAW_COLUMN_ALIASES)

_TEST_TYPE_HEADER_ALIASES = {
    _normalize_token(alias)
    for alias in (
        "test_type",
        "test",
        "test name",
        "testname",
        "soil_test",
    )
}

_TEST_TYPE_ALIASES: Dict[str, str] = {
    _normalize_token(test_type): test_type for test_type in VALID_TEST_TYPES
}

for display_name, internal_name in TEST_NAME_TO_TYPE.items():
    _TEST_TYPE_ALIASES[_normalize_token(display_name)] = internal_name

for alias, internal_name in {
    "directsimple": "direct_shear",
    "directsimpleshear": "direct_shear",
    "directshear": "direct_shear",
    "dss": "direct_shear",
}.items():
    _TEST_TYPE_ALIASES[_normalize_token(alias)] = internal_name


def _canonical_test_type(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = _normalize_token(value)
    if not normalized:
        return None
    return _TEST_TYPE_ALIASES.get(normalized)


def get_expected_columns_for_test_type(test_type: Optional[str]) -> List[str]:
    canonical_test_type = _canonical_test_type(test_type)
    if canonical_test_type is None:
        return []
    return list(_EXPECTED_COLUMNS_BY_TEST.get(canonical_test_type, []))


def _map_column_name_to_canonical_key(column_name: str) -> Optional[str]:
    normalized = _normalize_token(column_name)
    if not normalized:
        return None

    direct_match = _COLUMN_ALIASES.get(normalized)
    if direct_match is not None:
        return direct_match

    trimmed = normalized
    for suffix in (
        "kpa",
        "knm2",
        "mpa",
        "pa",
        "percent",
        "pct",
        "hours",
        "hour",
        "seconds",
        "second",
        "sec",
        "s",
    ):
        if trimmed.endswith(suffix) and len(trimmed) > len(suffix) + 1:
            candidate = trimmed[: -len(suffix)]
            mapped = _COLUMN_ALIASES.get(candidate)
            if mapped is not None:
                return mapped

    best_match: Optional[str] = None
    best_match_len = 0
    for alias_token, canonical_key in _COLUMN_ALIASES.items():
        if len(alias_token) < 3:
            continue
        if alias_token in normalized and len(alias_token) > best_match_len:
            best_match = canonical_key
            best_match_len = len(alias_token)

    return best_match


def _parse_float(value: str, line_number: int, column_name: str) -> Optional[float]:
    stripped = (value or "").strip()
    if not stripped:
        return None

    compact = stripped.replace(" ", "")
    if "," in compact and "." not in compact:
        compact = compact.replace(",", ".")
    elif "," in compact and "." in compact:
        compact = compact.replace(",", "")

    try:
        return float(compact)
    except ValueError as exc:
        raise ValueError(
            f"Invalid numeric value '{value}' in column '{column_name}' at line {line_number}"
        ) from exc


def _compute_missing_sigma_diff(results: Dict[str, List[float]]) -> None:
    if "sigma1_sigma3_diff" in results:
        return

    sigma_1 = results.get("sigma_1")
    sigma_3 = results.get("sigma_3")
    if not sigma_1 or not sigma_3:
        q_values = results.get("Deviatoric Stress")
        if q_values:
            results["sigma1_sigma3_diff"] = [abs(v) for v in q_values]
        return

    n = min(len(sigma_1), len(sigma_3))
    if n <= 0:
        return

    results["sigma1_sigma3_diff"] = [
        abs(sigma_1[index] - sigma_3[index]) for index in range(n)
    ]


def _detect_csv_dialect(
    sample: str,
) -> type[csv.Dialect] | csv.Dialect:
    if not sample or len(sample.strip()) == 0:
        return csv.excel

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t |")
        if dialect:
            return dialect
    except csv.Error:
        pass

    first_line = sample.split("\n")[0] if sample else ""
    if not first_line:
        return csv.excel

    delimiter_counts: Dict[str, int] = {
        ",": first_line.count(","),
        ";": first_line.count(";"),
        "\t": first_line.count("\t"),
        "|": first_line.count("|"),
    }

    best_delimiter = max(
        delimiter_counts, key=lambda delimiter: delimiter_counts[delimiter]
    )
    if delimiter_counts[best_delimiter] == 0:
        return csv.excel

    class CustomDialect(csv.Dialect):
        delimiter = best_delimiter
        quotechar = '"'
        doublequote = True
        skipinitialspace = False
        lineterminator = "\r\n"
        quoting = csv.QUOTE_MINIMAL

    return CustomDialect


def _decode_csv_bytes(csv_bytes: bytes, csv_file: Path) -> str:
    if not csv_bytes:
        raise ValueError(f"CSV file is empty: {csv_file}")

    decode_errors: List[str] = []
    for encoding in (
        "utf-8-sig",
        "utf-16",
        "utf-16-le",
        "utf-16-be",
        "cp1252",
        "latin-1",
    ):
        try:
            decoded = csv_bytes.decode(encoding)
        except UnicodeDecodeError as exc:
            decode_errors.append(f"{encoding}: {exc}")
            continue

        if decoded.count("\x00") > max(1, len(decoded) // 20):
            continue

        return decoded

    details = (
        "; ".join(decode_errors[:3]) if decode_errors else "unknown decoding error"
    )
    raise ValueError(
        f"Could not decode CSV file '{csv_file}'. "
        "Supported encodings include UTF-8, UTF-16, Windows-1252, and latin-1."
        f"Details: {details}"
    )


def _validate_csv_file(csv_file: Path) -> None:
    if not csv_file.exists() or not csv_file.is_file():
        raise ValueError(f"CSV file not found: {csv_file}")

    suffix = csv_file.suffix.lower()
    if suffix in {".xlsx", ".xls", ".xlsm", ".xlsb"}:
        raise ValueError(
            f"'{csv_file.name}' is an Excel workbook. "
            "Please export it to a .csv file and import that CSV file."
        )
    if suffix and suffix != ".csv":
        raise ValueError(
            f"Unsupported file type '{suffix}'. Please select a .csv file."
        )


def _read_csv_fieldnames(csv_file: Path) -> List[str]:
    _validate_csv_file(csv_file)

    csv_text = _decode_csv_bytes(csv_file.read_bytes(), csv_file)
    csv_stream = io.StringIO(csv_text, newline="")

    sample = csv_stream.read(2048)
    csv_stream.seek(0)

    dialect = _detect_csv_dialect(sample)
    reader = csv.DictReader(csv_stream, dialect=dialect)

    if not reader.fieldnames:
        raise ValueError("CSV file has no header row")

    return [h for h in reader.fieldnames if h is not None]


def get_csv_headers(csv_file: Path) -> List[str]:
    return _read_csv_fieldnames(csv_file)


def suggest_csv_column_mapping(
    headers: List[str], expected_columns: Optional[List[str]] = None
) -> Dict[str, str]:
    expected = set(expected_columns or [])
    mapping: Dict[str, str] = {}

    for header in headers:
        canonical_key = _map_column_name_to_canonical_key(header)
        if canonical_key is None:
            continue
        if expected and canonical_key not in expected:
            continue
        if canonical_key in mapping:
            continue
        mapping[canonical_key] = header

    return mapping


def _build_mapped_columns(
    file_headers: List[str], column_mapping: Optional[Dict[str, str]] = None
) -> tuple[Optional[str], Dict[str, str]]:
    test_type_column: Optional[str] = None
    mapped_columns: Dict[str, str] = {}

    for column_name in file_headers:
        normalized = _normalize_token(column_name)
        if normalized in _TEST_TYPE_HEADER_ALIASES and test_type_column is None:
            test_type_column = column_name
            continue

        canonical_key = _map_column_name_to_canonical_key(column_name)
        if canonical_key is None:
            continue
        if canonical_key in mapped_columns.values():
            continue
        mapped_columns[column_name] = canonical_key

    if column_mapping:
        header_set = set(file_headers)
        for canonical_key, source_column in column_mapping.items():
            if canonical_key not in _RAW_COLUMN_ALIASES:
                continue
            selected_source = (source_column or "").strip()
            if not selected_source:
                continue
            if selected_source not in header_set:
                raise ValueError(
                    f"Mapped source column '{selected_source}' was not found in CSV headers"
                )
            for existing_source, existing_canonical in list(mapped_columns.items()):
                if existing_canonical == canonical_key:
                    mapped_columns.pop(existing_source, None)
            mapped_columns[selected_source] = canonical_key

    if not mapped_columns:
        discovered_headers = ", ".join(str(h) for h in file_headers)
        raise ValueError(
            "CSV does not contain recognized columns for lab result import. "
            f"Detected headers: {discovered_headers}."
        )

    return test_type_column, mapped_columns


def _build_source_column_targets_for_unspecified_test_type(
    mapped_columns: Dict[str, str],
    default_test_type_internal: Optional[str],
) -> Dict[str, List[str]]:
    source_column_targets: Dict[str, List[str]] = {}
    expected_columns_for_selected_test = set(
        _EXPECTED_COLUMNS_BY_TEST.get(default_test_type_internal or "", [])
    )
    if not any(
        canonical_key in expected_columns_for_selected_test
        for canonical_key in mapped_columns.values()
    ):
        raise ValueError(
            "CSV does not contain recognized columns for the selected test type"
        )

    for source_column, canonical_key in mapped_columns.items():
        if (
            default_test_type_internal is not None
            and canonical_key in expected_columns_for_selected_test
        ):
            source_column_targets[source_column] = [default_test_type_internal]
        else:
            source_column_targets[source_column] = []

    return source_column_targets


def _get_row_test_type(
    row: Dict[str, Any],
    test_type_column: Optional[str],
    default_test_type_internal: Optional[str],
    line_number: int,
) -> Optional[str]:
    if test_type_column is not None:
        raw_test_type = (row.get(test_type_column) or "").strip()
        if raw_test_type:
            row_test_type = _canonical_test_type(raw_test_type)
            if row_test_type is None:
                raise ValueError(
                    f"Unknown test type '{raw_test_type}' at line {line_number}"
                )
            return row_test_type

    return default_test_type_internal


def _import_row_values_to_results(
    reader: csv.DictReader,
    mapped_columns: Dict[str, str],
    default_test_type_internal: Optional[str],
    test_type_column: Optional[str],
    source_column_targets: Dict[str, List[str]],
    experimental_by_test: Dict[str, Dict[str, List[float]]],
) -> bool:
    imported_any_value = False

    for line_number, row in enumerate(reader, start=2):
        row_test_type = _get_row_test_type(
            row, test_type_column, default_test_type_internal, line_number
        )
        if row_test_type is None:
            continue

        for source_column, canonical_key in mapped_columns.items():
            numeric_value = _parse_float(
                row.get(source_column, ""), line_number, source_column
            )
            if numeric_value is None:
                continue

            target_test_types = [row_test_type]
            if test_type_column is None:
                target_test_types = source_column_targets.get(source_column, [])

            if not target_test_types:
                continue

            imported_any_value = True
            for target_test_type in target_test_types:
                per_test_results = experimental_by_test.setdefault(target_test_type, {})
                per_test_results.setdefault(canonical_key, []).append(numeric_value)

    return imported_any_value


def parse_csv_lab_results(
    csv_file: Path,
    default_test_type: Optional[str] = None,
    column_mapping: Optional[Dict[str, str]] = None,
) -> Dict[str, Dict[str, List[float]]]:
    _validate_csv_file(csv_file)

    default_test_type_internal = _canonical_test_type(default_test_type)

    csv_text = _decode_csv_bytes(csv_file.read_bytes(), csv_file)
    csv_stream = io.StringIO(csv_text, newline="")

    sample = csv_stream.read(2048)
    csv_stream.seek(0)

    dialect = _detect_csv_dialect(sample)

    reader = csv.DictReader(csv_stream, dialect=dialect)
    if not reader.fieldnames:
        raise ValueError("CSV file has no header row")

    file_headers = [h for h in reader.fieldnames if h is not None]
    test_type_column, mapped_columns = _build_mapped_columns(
        file_headers, column_mapping
    )

    if test_type_column is None and default_test_type_internal is None:
        raise ValueError(
            "CSV must include a test_type column when no active test type is available"
        )

    source_column_targets = {}
    if test_type_column is None:
        source_column_targets = _build_source_column_targets_for_unspecified_test_type(
            mapped_columns, default_test_type_internal
        )

    experimental_by_test: Dict[str, Dict[str, List[float]]] = {}
    imported_any_value = _import_row_values_to_results(
        reader,
        mapped_columns,
        default_test_type_internal,
        test_type_column,
        source_column_targets,
        experimental_by_test,
    )

    if not imported_any_value:
        raise ValueError("CSV does not contain any numeric values to import")

    for results in experimental_by_test.values():
        _compute_missing_sigma_diff(results)

    return experimental_by_test
