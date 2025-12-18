# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl


#-----------------------UI labels---------------------------

# Application data
APP_TITLE = "Deltares Soil Element Test Suite"
APP_VERSION = "Version 0.1.6 ~ Alpha Release"
APP_NAME = "SoilElementSuite"
APP_AUTHOR = "Deltares"

# General test types
TRIAXIAL = "Triaxial"
DIRECT_SHEAR = "Direct Simple Shear"
CRS = "CRS"

TEST_NAME_TO_TYPE = {
    TRIAXIAL: "triaxial",
    DIRECT_SHEAR: "direct_shear",
    CRS: "crs",
}

# Valid test types
VALID_TEST_TYPES: tuple[str, ...] = tuple(TEST_NAME_TO_TYPE.values())

# Valid drainage types
VALID_DRAINAGE_TYPES: tuple[str, ...] = ("drained", "undrained")

# Test image files
TEST_IMAGE_FILES = {
    TRIAXIAL: "Triaxial.png",
    DIRECT_SHEAR: "DSS.png",
    CRS: "CRS.png",
}

# Input labels
MAX_STRAIN_LABEL = "Maximum Strain |εᵧᵧ|"
INIT_PRESSURE_LABEL = "Initial effective cell pressure |σ'ₓₓ|"
STRESS_INC_LABEL = "Stress increment |σ'ᵧᵧ|"
NUM_STEPS_LABEL = "Number of steps"
DURATION_LABEL = "Duration"
STRAIN_INCREMENT_LABEL = "Strain inc."
STEPS_LABEL = "steps"

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
