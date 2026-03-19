# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import ctypes
import importlib
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk, scrolledtext, Menu
from typing import Dict, List, Optional

platformdirs_spec = importlib.util.find_spec("platformdirs")
if platformdirs_spec is not None:
    user_data_dir = importlib.import_module("platformdirs").user_data_dir
else:
    def user_data_dir(appname: str, appauthor: Optional[str] = None) -> str:
        if sys.platform == "win32":
            base_dir = Path(
                os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
            )
            app_dir = base_dir / appname
            if appauthor:
                app_dir = base_dir / appauthor / appname
            return str(app_dir)

        if sys.platform == "darwin":
            return str(Path.home() / "Library" / "Application Support" / appname)

        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        base_dir = Path(xdg_data_home) if xdg_data_home else Path.home() / ".local" / "share"
        return str(base_dir / appname)

from kratos_element_test.controller.element_test_controller import ElementTestController
from kratos_element_test.model.io.lab_results_csv_parser import (
    get_csv_headers,
    get_expected_columns_for_test_type,
    suggest_csv_column_mapping,
)
from kratos_element_test.view.ui_builder import GeotechTestUI
from kratos_element_test.view.ui_constants import (
    APP_TITLE,
    APP_VERSION,
    APP_NAME,
    APP_AUTHOR,
    SELECT_UDSM,
    LINEAR_ELASTIC,
    MOHR_COULOMB,
    HELP_MENU_FONT,
    DEFAULT_TKINTER_DPI,
    TYPE_TO_TEST_NAME,
    TEST_NAME_TO_TYPE,
)
from kratos_element_test.view.ui_logger import log_message
from kratos_element_test.view.ui_utils import asset_path, soil_models_dir

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
    "deltares.ElementTestSuite.ui"
)

data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
data_dir.mkdir(parents=True, exist_ok=True)

LICENSE_FLAG_PATH = data_dir / "license_accepted.flag"


class MainUI:
    def __init__(self):
        self._controller = ElementTestController(
            logger=log_message,
        )
        self.main_frame = None
        self._root = None

    def show_license_agreement(self, readonly=False):
        license_file_path = asset_path("license.txt")
        try:
            with open(license_file_path, "r", encoding="utf-8") as f:
                license_text = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load license file: {e}")
            os._exit(1)

        license_window = tk.Toplevel()
        license_window.title("Pre-Release License Agreement")
        license_window.geometry("800x600")
        license_window.grab_set()

        if not readonly:
            license_window.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))

        tk.Label(
            license_window,
            text="Pre-Release Software License Agreement",
            font=(HELP_MENU_FONT, 12, "bold"),
            pady=10,
        ).pack()

        tk.Label(
            license_window,
            text="Please review and accept the agreement to continue.",
            font=(HELP_MENU_FONT, 12, "bold"),
            pady=10,
        ).pack()

        text_area = scrolledtext.ScrolledText(
            license_window, wrap="word", font=("Courier", 10)
        )
        text_area.insert("1.0", license_text)
        text_area.config(state="disabled")
        text_area.pack(expand=True, fill="both", padx=10, pady=10)

        button_frame = tk.Frame(license_window)
        button_frame.pack(pady=10)

        if readonly:
            tk.Button(
                button_frame, text="Close", width=15, command=license_window.destroy
            ).pack()
        else:

            def accept():
                try:
                    with open(LICENSE_FLAG_PATH, "w") as f:
                        f.write("ACCEPTED")
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Could not save license acceptance: {e}"
                    )
                    os._exit(1)
                license_window.destroy()

            def decline():
                messagebox.showinfo(
                    "Exit",
                    "You must accept the license agreement to use this software.",
                )
                os._exit(0)

            tk.Button(button_frame, text="Accept", width=15, command=accept).pack(
                side="left", padx=10
            )
            tk.Button(button_frame, text="Decline", width=15, command=decline).pack(
                side="right", padx=10
            )

    def show_about_window(self):
        about_win = tk.Toplevel()
        about_win.title("About")
        about_win.geometry("500x400")
        about_win.resizable(False, False)
        about_win.grab_set()

        tk.Label(about_win, text=APP_TITLE, font=(HELP_MENU_FONT, 14, "bold")).pack(
            pady=(20, 5)
        )
        tk.Label(about_win, text=APP_VERSION, font=(HELP_MENU_FONT, 12)).pack(
            pady=(0, 5)
        )
        tk.Label(about_win, text="Powered by:", font=(HELP_MENU_FONT, 12)).pack(
            pady=(0, 5)
        )

        image_frame = tk.Frame(about_win)
        image_frame.pack(pady=10)

        try:
            path1 = asset_path("kratos.png")
            path2 = asset_path("deltares.png")

            photo1 = tk.PhotoImage(file=path1)
            photo2 = tk.PhotoImage(file=path2)

            label1 = tk.Label(image_frame, image=photo1)
            label1.image = photo1
            label1.pack(pady=2)

            label2 = tk.Label(image_frame, image=photo2)
            label2.image = photo2
            label2.pack(pady=15)

        except Exception:
            tk.Label(
                about_win, text="[One or both images could not be loaded]", fg="red"
            ).pack()

        tk.Label(
            about_win, text="Contact: kratos@deltares.nl", font=(HELP_MENU_FONT, 12)
        ).pack(pady=(0, 2))
        tk.Button(about_win, text="Close", command=about_win.destroy).pack(pady=10)

    def create_menu(self):

        last_model_source = LINEAR_ELASTIC
        root = tk.Tk()
        self._root = root

        root.bind_class("TCombobox", "<MouseWheel>", lambda e: "break")
        root.bind_class("TCombobox", "<Shift-MouseWheel>", lambda e: "break")

        pixels_per_inch = root.winfo_fpixels("1i")
        scaling_factor = pixels_per_inch / DEFAULT_TKINTER_DPI

        if scaling_factor > 1.25:
            root.tk.call("tk", "scaling", scaling_factor)

        menubar = Menu(root)
        root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=lambda: root.quit())
        menubar.add_cascade(label="File", menu=file_menu)

        export_menu = Menu(menubar, tearoff=0)
        export_menu.add_command(
            label="Export Results (Excel)", command=self._export_latest_results
        )
        menubar.add_cascade(label="Export", menu=export_menu)

        import_menu = Menu(menubar, tearoff=0)
        import_menu.add_command(
            label="Import Lab Results (experimental feature)",
            command=self._import_lab_results,
        )
        import_menu.add_command(
            label="Import CSV data",
            command=self._import_csv_data,
        )
        menubar.add_cascade(label="Import", menu=import_menu)

        about_menu = Menu(menubar, tearoff=0)
        about_menu.add_command(
            label="License", command=lambda: self.show_license_agreement(readonly=True)
        )
        about_menu.add_command(label="About", command=self.show_about_window)
        menubar.add_cascade(label="Help", menu=about_menu)

        if not os.path.exists(LICENSE_FLAG_PATH):
            self.show_license_agreement()

        try:
            icon_path = asset_path("icon.ico")
            root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Could not set icon: {e}")

        root.title(f"{APP_TITLE} - {APP_VERSION}")
        root.state("zoomed")
        root.resizable(True, True)

        top_frame = ttk.Frame(root, padding="10")
        top_frame.pack(side="top", fill="x")

        def _safe_udsm_initialdir() -> str:
            try:
                p = soil_models_dir()
                if p.is_dir():
                    return str(p)
            except Exception:
                pass

            root = Path.cwd().anchor
            return root if root else os.path.abspath(os.sep)

        def load_dll():
            self._controller.set_material_type("udsm")
            nonlocal last_model_source
            dll_path = filedialog.askopenfilename(
                title=SELECT_UDSM,
                initialdir=_safe_udsm_initialdir(),
                filetypes=[("DLL files", "*.dll")],
            )
            if not dll_path:
                messagebox.showerror("Error", "No DLL file selected.")
                model_source_var.set(last_model_source)
                return

            try:
                self._controller.parse_udsm(Path(dll_path))
            except Exception as e:
                messagebox.showerror("DLL Error", f"Failed to parse DLL: {e}")
                model_source_var.set(last_model_source)
                return
            last_model_source = SELECT_UDSM

            if self.main_frame:
                for widget in self.main_frame.winfo_children():
                    widget.destroy()
                self.main_frame.destroy()
            self.main_frame = GeotechTestUI(
                root,
                controller=self._controller,
                external_widgets=[model_source_menu],
            )

        def load_linear_elastic():
            self._controller.set_material_type("linear_elastic")
            nonlocal last_model_source
            last_model_source = LINEAR_ELASTIC

            if self.main_frame:
                for widget in self.main_frame.winfo_children():
                    widget.destroy()
                self.main_frame.destroy()

            self.main_frame = GeotechTestUI(
                root,
                controller=self._controller,
                external_widgets=[model_source_menu],
            )

        def load_mohr_coulomb():
            self._controller.set_material_type("mohr_coulomb")
            nonlocal last_model_source
            last_model_source = MOHR_COULOMB

            if self.main_frame:
                for widget in self.main_frame.winfo_children():
                    widget.destroy()
                self.main_frame.destroy()

            self.main_frame = GeotechTestUI(
                root,
                controller=self._controller,
                external_widgets=[model_source_menu],
            )

        def handle_model_source_selection(event):
            choice = model_source_var.get()
            if choice == SELECT_UDSM:
                load_dll()
            elif choice == LINEAR_ELASTIC:
                load_linear_elastic()
            elif choice == MOHR_COULOMB:
                load_mohr_coulomb()

        model_source_var = tk.StringVar(value="Select Model Source")
        model_source_menu = ttk.Combobox(
            top_frame,
            textvariable=model_source_var,
            values=[SELECT_UDSM, LINEAR_ELASTIC, MOHR_COULOMB],
            state="readonly",
        )
        model_source_menu.bind("<<ComboboxSelected>>", handle_model_source_selection)
        model_source_menu.pack(side="left", padx=5)

        def on_close():
            root.quit()
            root.destroy()
            os._exit(0)

        root.protocol("WM_DELETE_WINDOW", on_close)
        root.mainloop()

    def _export_latest_results(self):
        try:
            self._controller.export_latest_results()
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export Excel file.\n\n{e}")

    def _import_lab_results(self):
        try:
            py_path = filedialog.askopenfilename(
                title="Select lab results Python file",
                filetypes=[("Python files", "*.py")],
            )
            if not py_path:
                return

            self._controller.import_lab_results(Path(py_path))
            self.main_frame.redraw_plots()

        except Exception as e:
            messagebox.showerror(
                "Import Error", f"Failed to import lab results.\n\n{e}"
            )

    def _import_csv_data(self):
        try:
            current_test_display_name = self._controller.get_current_test_type()
            if not current_test_display_name or current_test_display_name.strip() == "":
                messagebox.showerror(
                    "Import Error",
                    "No active test selected. Please select a test (Triaxial, Direct Simple Shear, or CRS) "
                    "before importing CSV data.",
                )
                return

            csv_path = filedialog.askopenfilename(
                title="Select CSV data file",
                filetypes=[("CSV files", "*.csv")],
            )
            if not csv_path:
                return

            selected_file = Path(csv_path)
            if selected_file.suffix.lower() != ".csv":
                messagebox.showerror(
                    "Import Error",
                    "The selected file is not a CSV file. "
                    "Please choose a file with .csv extension.",
                )
                return

            file_headers = get_csv_headers(selected_file)
            
            current_test_internal_name = TEST_NAME_TO_TYPE.get(current_test_display_name)
            if not current_test_internal_name:
                messagebox.showerror(
                    "Import Error",
                    f"Unknown test type '{current_test_display_name}'.",
                )
                return
            
            expected_headers = get_expected_columns_for_test_type(current_test_internal_name)
            suggested_mapping = suggest_csv_column_mapping(
                file_headers, expected_headers
            )

            column_mapping = self._show_csv_header_mapping_popup(
                file_headers=file_headers,
                expected_headers=expected_headers,
                suggested_mapping=suggested_mapping,
                test_display_name=current_test_display_name,
            )
            if column_mapping is None:
                return

            imported_test_type = self._controller.import_csv_data(
                selected_file,
                column_mapping=column_mapping,
                target_test_type=current_test_internal_name,
            )

            imported_display_test = TYPE_TO_TEST_NAME.get(
                imported_test_type, imported_test_type
            )
            if self.main_frame and imported_display_test != current_test_display_name:
                self.main_frame.select_test(imported_display_test)

            if self.main_frame:
                self.main_frame.redraw_plots()

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import CSV data.\n\n{e}")

    def _show_csv_header_mapping_popup(
        self,
        file_headers: List[str],
        expected_headers: List[str],
        suggested_mapping: Dict[str, str],
        test_display_name: str = "",
    ) -> Optional[Dict[str, str]]:
        if self._root is None:
            return suggested_mapping

        if not expected_headers:
            return suggested_mapping

        dialog = tk.Toplevel(self._root)
        dialog.title("Map CSV headers")
        dialog.geometry("360x600")
        dialog.resizable(True, True)
        dialog.transient(self._root)
        dialog.grab_set()

        label_text = "Map CSV headers to the expected variables"
        if test_display_name:
            label_text += f" for {test_display_name}"
        ttk.Label(
            dialog,
            text=label_text,
        ).pack(anchor="w", padx=12, pady=(12, 8))

        preview_frame = ttk.Frame(dialog, padding="8")
        preview_frame.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(preview_frame, text="Headers found in file:").pack(anchor="w")

        preview_text = scrolledtext.ScrolledText(preview_frame, height=5, wrap="word")
        preview_text.pack(fill="x", expand=False, pady=(4, 0))
        preview_text.insert("1.0", "\n".join(file_headers))
        preview_text.config(state="disabled")

        mapping_frame = ttk.Frame(dialog, padding="8")
        mapping_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        ttk.Label(mapping_frame, text="Expected variable").grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 6)
        )
        ttk.Label(mapping_frame, text="CSV header").grid(
            row=0, column=1, sticky="w", pady=(0, 6)
        )

        selectable_headers = ["<skip>"] + file_headers
        vars_by_expected: Dict[str, tk.StringVar] = {}

        for idx, expected_key in enumerate(expected_headers, start=1):
            ttk.Label(mapping_frame, text=expected_key).grid(
                row=idx, column=0, sticky="w", padx=(0, 12), pady=3
            )
            selected_header = suggested_mapping.get(expected_key, "<skip>")
            if selected_header not in selectable_headers:
                selected_header = "<skip>"

            selected_var = tk.StringVar(value=selected_header)
            vars_by_expected[expected_key] = selected_var

            combobox = ttk.Combobox(
                mapping_frame,
                textvariable=selected_var,
                values=selectable_headers,
                state="readonly",
                width=48,
            )
            combobox.grid(row=idx, column=1, sticky="ew", pady=3)

        mapping_frame.columnconfigure(1, weight=1)

        action_frame = ttk.Frame(dialog, padding="8")
        action_frame.pack(fill="x", padx=8, pady=(0, 8))

        result: Dict[str, str] = {}
        is_confirmed = {"value": False}

        def _on_import():
            is_confirmed["value"] = True
            result.clear()
            selected_header_to_expected_keys: Dict[str, List[str]] = {}

            for expected_key, selected_var in vars_by_expected.items():
                selected = selected_var.get()
                if selected and selected != "<skip>":
                    result[expected_key] = selected

                    expected_keys = selected_header_to_expected_keys.setdefault(
                        selected, []
                    )
                    expected_keys.append(expected_key)

            # The parser keeps only the last mapping when one CSV header is assigned
            # to multiple expected variables. Warn users explicitly in the log output.
            for selected_header, expected_keys in selected_header_to_expected_keys.items():
                if len(expected_keys) <= 1:
                    continue

                kept_expected_key = expected_keys[-1]
                for ignored_expected_key in expected_keys[:-1]:
                    log_message(
                        f"Ignored mapping for '{ignored_expected_key}': CSV header "
                        f"'{selected_header}' is used more than once. "
                        f"Keeping '{kept_expected_key}'.",
                        "warn",
                    )

            dialog.destroy()

        def _on_cancel():
            dialog.destroy()

        ttk.Button(action_frame, text="Import", command=_on_import).pack(
            side="right", padx=(8, 0)
        )
        ttk.Button(action_frame, text="Cancel", command=_on_cancel).pack(side="right")

        dialog.wait_window()

        if not is_confirmed["value"]:
            return None
        return result


if __name__ == "__main__":
    ui = MainUI()
    ui.create_menu()
