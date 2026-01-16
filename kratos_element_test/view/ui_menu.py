# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext, Menu
from platformdirs import user_data_dir
from pathlib import Path

from kratos_element_test.controller.element_test_controller import ElementTestController
from kratos_element_test.plotters.matplotlib_plotter import MatplotlibPlotter
from kratos_element_test.view.ui_builder import GeotechTestUI
from kratos_element_test.model.io.udsm_parser import udsm_parser
from kratos_element_test.view.ui_utils import _asset_path
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
)
from kratos_element_test.view.ui_logger import log_message

import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
    "deltares.ElementTestSuite.ui"
)

data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
data_dir.mkdir(parents=True, exist_ok=True)

LICENSE_FLAG_PATH = data_dir / "license_accepted.flag"


class MainUI:
    def __init__(self):
        self.main_frame = None

    def show_license_agreement(self, readonly=False):
        license_file_path = _asset_path("license.txt")
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
            path1 = _asset_path("kratos.png")
            path2 = _asset_path("deltares.png")

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
        controller = ElementTestController(
            logger=log_message,
            plotter_factory=lambda axes: MatplotlibPlotter(axes, logger=log_message),
        )

        last_model_source = LINEAR_ELASTIC
        root = tk.Tk()

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
            label="Export Results (Excel)", command=controller.export_latest_results
        )
        menubar.add_cascade(label="Export", menu=export_menu)

        about_menu = Menu(menubar, tearoff=0)
        about_menu.add_command(
            label="License", command=lambda: self.show_license_agreement(readonly=True)
        )
        about_menu.add_command(label="About", command=self.show_about_window)
        menubar.add_cascade(label="Help", menu=about_menu)

        if not os.path.exists(LICENSE_FLAG_PATH):
            self.show_license_agreement()

        try:
            icon_path = _asset_path("icon.ico")
            root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Could not set icon: {e}")

        root.title(f"{APP_TITLE} - {APP_VERSION}")
        root.state("zoomed")
        root.resizable(True, True)

        top_frame = ttk.Frame(root, padding="10")
        top_frame.pack(side="top", fill="x")

        def load_dll():
            nonlocal last_model_source
            dll_path = filedialog.askopenfilename(
                title=SELECT_UDSM, filetypes=[("DLL files", "*.dll")]
            )
            if not dll_path:
                messagebox.showerror("Error", "No DLL file selected.")
                model_source_var.set(last_model_source)
                return

            try:
                model_dict = udsm_parser(dll_path)
            except Exception as e:
                messagebox.showerror("DLL Error", f"Failed to parse DLL: {e}")
                model_source_var.set(last_model_source)
                return
            last_model_source = SELECT_UDSM

            if self.main_frame:
                for widget in self.main_frame.winfo_children():
                    widget.destroy()
                self.main_frame.destroy()
            controller.clear_results()
            self.main_frame = GeotechTestUI(
                root,
                test_name="Triaxial",
                dll_path=dll_path,
                model_dict=model_dict,
                controller=controller,
                external_widgets=[model_source_menu],
            )

        def load_linear_elastic():
            nonlocal last_model_source
            model_dict = {
                "model_name": [LINEAR_ELASTIC],
                "num_params": [2],
                "param_names": [["Young's Modulus", "Poisson's Ratio"]],
                "param_units": [["kN/m²", "–"]],
            }
            last_model_source = LINEAR_ELASTIC

            if self.main_frame:
                for widget in self.main_frame.winfo_children():
                    widget.destroy()
                self.main_frame.destroy()

            controller.clear_results()
            self.main_frame = GeotechTestUI(
                root,
                test_name="Triaxial",
                dll_path=None,
                model_dict=model_dict,
                controller=controller,
                external_widgets=[model_source_menu],
            )

        def load_mohr_coulomb():
            nonlocal last_model_source
            model_dict = {
                "model_name": [MOHR_COULOMB],
                "num_params": [4],
                "param_names": [
                    [
                        "Young's Modulus",
                        "Poisson's Ratio",
                        "Cohesion",
                        "Friction Angle",
                        "Tensile Strength",
                        "Dilatancy Angle",
                    ]
                ],
                "param_units": [["kN/m²", "-", "kN/m²", "deg", "kN/m²", "deg"]],
            }
            last_model_source = MOHR_COULOMB

            if self.main_frame:
                for widget in self.main_frame.winfo_children():
                    widget.destroy()
                self.main_frame.destroy()

            controller.clear_results()
            self.main_frame = GeotechTestUI(
                root,
                test_name="Triaxial",
                dll_path=None,
                model_dict=model_dict,
                controller=controller,
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

        def refresh_plot_frame():
            root.update_idletasks()
            root.event_generate("<Configure>")

        root.protocol("WM_DELETE_WINDOW", on_close)
        root.mainloop()


if __name__ == "__main__":
    ui = MainUI()
    ui.create_menu()
