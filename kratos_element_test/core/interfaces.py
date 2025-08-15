# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

from typing import Protocol, Iterable, Optional, Callable

Logger = Callable[[str, str], None]


class Plotter(Protocol):
    def triaxial(self,
                 eps_yy: Iterable[float],
                 diff_sig: Iterable[float],
                 sigma1: Iterable[float],
                 sigma3: Iterable[float],
                 mean_stress: Iterable[float],
                 von_mises: Iterable[float],
                 cohesion: Optional[float],
                 phi: Optional[float]) -> None: ...

    def direct_shear(self, *args, **kwargs) -> None: ...
