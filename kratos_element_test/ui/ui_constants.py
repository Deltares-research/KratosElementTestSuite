# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl


#-----------------------UI labels---------------------------

# Application data
APP_TITLE = "Deltares Soil Element Test Suite"
APP_VERSION = "Version 0.1.3 ~ Alpha Release"
APP_NAME = "SoilElementSuite"
APP_AUTHOR = "Deltares"

# General test types
TRIAXIAL = "Triaxial"
DIRECT_SHEAR = "Direct Simple Shear"

TEST_NAME_TO_TYPE = {
    TRIAXIAL: "triaxial",
    DIRECT_SHEAR: "direct_shear",
}

# Valid test types
VALID_TEST_TYPES: tuple[str, ...] = ("triaxial", "direct_shear")

# Valid drainage types
VALID_DRAINAGE_TYPES: tuple[str, ...] = ("drained", "undrained")

# Input labels
MAX_STRAIN_LABEL = "Maximum Strain |εᵧᵧ|"
INIT_PRESSURE_LABEL = "Initial effective cell pressure |σ'ₓₓ|"
STRESS_INC_LABEL = "Stress increment |σ'ᵧᵧ|"
NUM_STEPS_LABEL = "Number of steps"
DURATION_LABEL = "Duration"

# Units
FL2_UNIT_LABEL = "kN/m²"
SECONDS_UNIT_LABEL = "s"
PERCENTAGE_UNIT_LABEL = "%"
WITHOUT_UNIT_LABEL = ""

# Menu labels
SELECT_UDSM = "Select UDSM File"
LINEAR_ELASTIC = "Linear Elastic Model"

# Font labels
HELP_MENU_FONT = "Segoe UI"
INPUT_SECTION_FONT = "Arial"

# Default tkinter values
DEFAULT_TKINTER_DPI = 72
