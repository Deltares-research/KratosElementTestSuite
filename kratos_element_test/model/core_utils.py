# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl


def _fallback_log(msg: str, level: str = "info") -> None:
    """
    Fallback logging function that prints messages to the console.
    """
    print(f"{level.upper()}: {msg}")


def seconds_to_hours(seconds: float) -> float:
    return seconds / 3600.0


def seconds_list_to_hours_list(second_list: list[float]) -> list[float]:
    return [seconds_to_hours(second) for second in second_list]


def hours_to_seconds(hours: float) -> float:
    return hours * 3600.0
