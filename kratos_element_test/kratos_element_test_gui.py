# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import os
import sys

from kratos_element_test.ui_menu import create_menu

if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    print("Adding Directory")
    dll_directory = os.path.abspath("./libs")
    # Add the dll_directory to the PATH environment variable temporarily
    os.environ['PATH'] = dll_directory + ';' + os.environ.get('PATH', '')
    # Now you can load DLLs from that directory in this Python session or subprocesses
    print("Temporary PATH:", os.environ['PATH'])

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    try:
        create_menu()
    except ImportError as e:
        print(f"[ERROR] Could not run GUI: {e}. Make sure the GeoMechanicsApplication is built and installed correctly.")
        sys.exit(1)

if __name__ == "__main__":
    main()
