# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import re


def _fallback_log(msg: str, level: str = "info"):
    print(f"{level.upper()}: {msg}")

class MdpaEditor:
    def __init__(self, mdpa_path, logger=None):
        # logger :  Optional logger function to log messages.
        #    Callable with signature ``logger(message: str, level: str = 'info') -> None``.
        #    If not provided, a no-op logger is used.
        self.mdpa_path = mdpa_path
        self._log = logger or _fallback_log
        try:
            with open(self.mdpa_path, 'r') as f:
                self.raw_text = f.read()
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {self.mdpa_path}")

    def save(self):
        with open(self.mdpa_path, 'w') as f:
            f.write(self.raw_text)

    def _replacer_factory(self, variable_value):
        def replacer(match):
            return f"{variable_value:.4f}"
        return replacer

    def update_maximum_strain(self, maximum_strain):
        pattern = r'\$maximum_strain\b'
        prescribed_displacement = -maximum_strain / 100

        replacer = self._replacer_factory(prescribed_displacement)
        new_text, count = re.subn(pattern, replacer, self.raw_text)
        if count == 0:
            self._log("Could not update maximum strain.", "warn")
        else:
            self.raw_text = new_text
            self.save()

    def update_initial_effective_cell_pressure(self, initial_effective_cell_pressure):
        pattern = r'\$initial_effective_cell_pressure\b'

        replacer = self._replacer_factory(initial_effective_cell_pressure)
        new_text, count = re.subn(pattern, replacer, self.raw_text)
        if count == 0:
            self._log("Could not update initial effective cell pressure.", "warn")
        else:
            self.raw_text = new_text
            MdpaEditor.save(self)
            self.save()

    def update_first_timestep(self, num_steps, end_time):
        first_timestep = end_time / num_steps
        pattern = r'\$first_timestep\b'

        replacer = self._replacer_factory(first_timestep)
        new_text, count = re.subn(pattern, replacer, self.raw_text)
        if count == 0:
            self._log("Could not apply the first time step.", "warn")
        else:
            self.raw_text = new_text
            MdpaEditor.save(self)
            self.save()

    def update_end_time(self, end_time):
        pattern = r'\$end_time\b'
        replacement = str(end_time)

        new_text, count = re.subn(pattern, replacement, self.raw_text)

        if count == 0:
            self._log("Could not update the end time.", "warn")
        else:
            self.raw_text = new_text
            MdpaEditor.save(self)
            self.save()

    def update_middle_maximum_strain(self, maximum_strain):
        pattern = r'\$middle_maximum_strain\b'
        prescribed_middle_displacement = (-maximum_strain / 2) / 100

        replacer = self._replacer_factory(prescribed_middle_displacement)
        new_text, count = re.subn(pattern, replacer, self.raw_text)
        if count == 0:
            self._log("Could not update middle maximum strain.", "warn")
        else:
            self.raw_text = new_text
            MdpaEditor.save(self)
            self.save()
