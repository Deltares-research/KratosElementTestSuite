# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl


def _fallback_log(msg: str, level: str = "info") -> None:
    """
        Fallback logging function that prints messages to the console.
    """
    print(f"{level.upper()}: {msg}")
