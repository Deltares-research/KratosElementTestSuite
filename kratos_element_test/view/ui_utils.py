# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

from pathlib import Path


def _asset_path(name: str) -> str:
    """
    Return an absolute path to a UI asset.

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
