# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

from pathlib import Path


def asset_path(name: str) -> str:
    """
    Returns an absolute path to a UI asset.

    Search order:
      1) <this_dir>/assets/<name>
      2) <this_dir>/../assets/<name>  (project-level assets)
    Falls back to <this_dir>/assets/<name> if not found.
    """
    ui_dir = Path(__file__).resolve().parent
    candidates = [ui_dir / "assets" / name, ui_dir.parent / "assets" / name]
    for p in candidates:
        if p.exists():
            return str(p)
    raise FileNotFoundError(
        f"Asset '{name}' not found. Tried: {', '.join(str(p) for p in candidates)}"
    )


def soil_models_dir() -> str:
    """
    Returns an absolute path to the shipped soil_models directory.
    """
    package_root = Path(__file__).resolve().parents[1]
    soil_models_dir = package_root / "model" / "simulation_assets" / "soil_models"
    if soil_models_dir.is_dir():
        return str(soil_models_dir)
    raise FileNotFoundError(
        "Soil models directory not found. Expected at: " f"{soil_models_dir}"
    )
