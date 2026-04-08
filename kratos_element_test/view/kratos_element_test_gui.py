# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import os
import sys
from pathlib import Path

# Allow running this file directly without requiring python -m.
if __package__ in (None, ""):
    package_parent = Path(__file__).resolve().parents[2]
    package_parent_str = str(package_parent)
    if package_parent_str not in sys.path:
        sys.path.insert(0, package_parent_str)

from kratos_element_test.view.ui_menu import MainUI


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    try:
        ui = MainUI()
        ui.create_menu()
    except ImportError as e:
        print(
            f"[ERROR] Could not run GUI: {e}. Make sure the GeoMechanicsApplication is built and installed correctly."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
