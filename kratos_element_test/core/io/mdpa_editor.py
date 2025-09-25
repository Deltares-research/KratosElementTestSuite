# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import re
from kratos_element_test.core.core_utils import _fallback_log


class MdpaEditor:
    def __init__(self, mdpa_path, logger=None):
        """
        Initialize the MdpaEditor

        Parameters
        ----------
        mdpa_path : str
            Path to the mdpa file containing the model mesh and definitions.
        logger : Callable[[str, str], None], optional
            A logging function that takes (message: str, level: str).
            Expected levels are "info", "warn", and "error".
            If not provided, a simple console-printing fallback is used.
        """
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
            self.save()

    def update_first_timestep(self, first_timestep):

        pattern = r'\$first_timestep\b'

        replacer = self._replacer_factory(first_timestep)
        new_text, count = re.subn(pattern, replacer, self.raw_text)
        if count == 0:
            self._log("Could not apply the first time step.", "warn")
        else:
            self.raw_text = new_text
            self.save()

    def update_end_time(self, end_time):
        pattern = r'\$end_time\b'
        replacement = str(end_time)

        new_text, count = re.subn(pattern, replacement, self.raw_text)

        if count == 0:
            self._log("Could not update the end time.", "warn")
        else:
            self.raw_text = new_text
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
            self.save()

    def insert_displacement_tables(self, durations: list[float], strains: list[float]):
        """
        Inserts displacement tables into the .mdpa file, one per stage.
        """
        tables = []
        cumulative_time = 0.0
        cumulative_strain = 0.0

        for i, (duration, strain) in enumerate(zip(durations, strains)):
            start_time = cumulative_time
            end_time = cumulative_time + duration
            displacement = (strain / 100)

            table = (
                f"Begin Table {i + 1} TIME DISPLACEMENT_Y\n"
                f"  {start_time:.1f} 0.0\n"
                f"  {end_time:.1f} {displacement :.6f}\n"
                f"End Table\n"
            )
            tables.append(table)

            cumulative_time = end_time
            cumulative_strain += strain

        if not tables:
            self._log("No tables to insert.", "warn")
            return

        table_block = "\n".join(tables) + "\n\n"
        self.raw_text = table_block + self.raw_text
        self.save()

    def update_top_displacement_tables(self, num_tables: int):
        """
        Replaces the content of the SubModelPartTables section in top_displacement
        with the correct number of table indices (1-based).
        """
        indent = " " * 12
        new_lines = "\n".join(f"{indent}{i}" for i in range(1, num_tables + 1))

        pattern = (
            r"(Begin SubModelPart top_displacement\b(?:.|\n)*?Begin SubModelPartTables\s*\n)"
            r"(.*?)"
            r"(\s*End SubModelPartTables)"
        )

        def replacer(match):
            return f"{match.group(1)}{new_lines}\n{match.group(3)}"

        updated_text, count = re.subn(pattern, replacer, self.raw_text, flags=re.DOTALL)

        if count == 0:
            self._log("Could not update SubModelPartTables for top_displacement.", "warn")
        else:
            self.raw_text = updated_text
            self.save()
