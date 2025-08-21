# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

# Fallback logging function that prints messages to the console.
def _fallback_log(msg: str, level: str = "info") -> None:
    print(f"{level.upper()}: {msg}")