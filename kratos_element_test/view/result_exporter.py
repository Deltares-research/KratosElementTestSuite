# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import numpy as np
import pandas as pd
from tkinter import filedialog, messagebox
from pathlib import Path
from kratos_element_test.view.result_registry import PLOT_MAPPING


def _build_sheet_df(
    results: dict, y_key: str, x_key: str, y_label: str, x_label: str
) -> pd.DataFrame | None:
    if y_key not in {"delta_sigma", "shear_xy_abs", "mohr_circle"} and x_key not in {
        "gamma_xy_abs",
        None,
    }:
        if y_key in results and x_key in results:
            x = results[x_key]
            y = results[y_key]
            if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
                n = min(len(x), len(y))
                return pd.DataFrame({x_label: x[:n], y_label: y[:n]})
        return None

    if y_key == "delta_sigma":
        s1, s3, yy = (
            results.get("sigma1"),
            results.get("sigma3"),
            results.get("yy_strain"),
        )
        if s1 and s3 and yy:
            ds = np.abs(np.asarray(s1) - np.asarray(s3))
            n = min(len(ds), len(yy))
            return pd.DataFrame({x_label: np.asarray(yy)[:n], y_label: ds[:n]})
        return None

    if x_key == "gamma_xy_abs" and y_key == "shear_xy_abs":
        exy = results.get("shear_strain_xy")
        txy = results.get("shear_xy")
        if exy and txy:
            gamma = 2.0 * np.asarray(exy)
            tau = np.asarray(txy)
            return pd.DataFrame({x_label: np.abs(gamma), y_label: np.abs(tau)})
        return None

    if y_key == "mohr_circle":
        s1, s3 = results.get("sigma1"), results.get("sigma3")
        if s1 and s3 and len(s1) > 0 and len(s3) > 0:
            sigma_1 = float(s1[-1])
            sigma_3 = float(s3[-1])
            center = 0.5 * (sigma_1 + sigma_3)
            radius = 0.5 * (sigma_1 - sigma_3)
            theta = np.linspace(0.0, np.pi, 400)
            sigma = center + radius * np.cos(theta)
            tau = -radius * np.sin(theta)
            return pd.DataFrame({x_label: sigma, y_label: tau})
        return None

    return None


def export_excel_by_test_type(
    results: dict, test_type: str, excel_path: str | None = None
) -> None:
    if test_type not in PLOT_MAPPING:
        messagebox.showerror("Export Error", f"Unknown test type: {test_type}")
        return

    if not excel_path:
        default_name = f"{test_type}_results.xlsx"
        excel_path = filedialog.asksaveasfilename(
            title="Save Results as Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            initialfile=default_name,
        )
    if not excel_path:
        return

    mapping = PLOT_MAPPING[test_type]
    Path(excel_path).parent.mkdir(parents=True, exist_ok=True)

    written_any = False
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for idx, (y_key, x_key, y_label, x_label) in enumerate(mapping, start=1):
            df = _build_sheet_df(results, y_key, x_key, y_label, x_label)
            if df is None or df.empty:
                continue
            sheet_name = f"Plot {idx}"
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            written_any = True

    if written_any:
        messagebox.showinfo("Export", f"Exported Excel:\n{excel_path}")
    else:
        messagebox.showwarning(
            "Export", "No matching data found to export for this test."
        )
