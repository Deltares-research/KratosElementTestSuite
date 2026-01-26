# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import re
import json
from kratos_element_test.model.core_utils import _fallback_log


class ProjectParameterEditor:
    def __init__(self, json_path, logger=None):
        """
        Initialize the ProjectParameterEditor

        Parameters
        ----------
        json_path : str
            Path to the JSON file containing project properties.
        logger : Callable[[str, str], None], optional
            A logging function that takes (message: str, level: str).
            Expected levels are "info", "warn", and "error".
            If not provided, a simple console-printing fallback is used.
        """
        self.json_path = json_path
        self._log = logger or _fallback_log
        with open(self.json_path, 'r') as f:
            self.raw_text = f.read()

    def _write_back(self):
        with open(self.json_path, 'w') as f:
            f.write(self.raw_text)

    def _load_json(self):
        try:
            return json.loads(self.raw_text)
        except json.JSONDecodeError:
            raise RuntimeError("Invalid JSON structure.")

    def update_nested_value(self, module_name, key, new_list):
        try:
            data = json.loads(self.raw_text)

            loads_list = data.get("processes", {}).get("loads_process_list", [])
            for process in loads_list:
                if (
                    process.get("python_module") == module_name
                    and key in process.get("Parameters", {})
                ):
                    process["Parameters"][key] = new_list
                    self.raw_text = json.dumps(data, indent=4)
                    self._write_back()
                    return

            self._log(f"Could not find '{key}' under '{module_name}'.", "warn")

        except Exception as e:
            raise RuntimeError(f"Failed to update '{key}' under '{module_name}': {e}") from e

    def update_property(self, property_name, new_value):
        pattern = rf'("{property_name}"\s*:\s*)([0-9eE+\.\-]+)'
        replacement = rf'\g<1>{new_value}'
        self.raw_text, count = re.subn(pattern, replacement, self.raw_text)
        if count == 0:
            self._log(f"Could not find '{property_name}' to update.", "warn")
        elif count > 1:
            self._log(f"Multiple occurrences of '{property_name}' found. Updated all {count}.", "warn")
        self._write_back()

    def update_stage_timings(self, end_times: list[float], step_counts: list[int], start_time: float = 0.0):
        """
        Applies staged start/end time logic.
        end_times: List of end_time values for each stage.
        step_counts: List of step counts for each stage.
        start_time: The start time of the first stage (default is 0.0).
        """
        try:
            data = self._load_json()

            stage_names = list(data["stages"].keys())

            for stage_name, end_time, step_count in zip(stage_names, end_times, step_counts, strict=True):
                stage = data["stages"][stage_name]
                settings = stage.get("stage_settings", {})

                settings.setdefault("problem_data", {})["start_time"] = start_time
                settings["problem_data"]["end_time"] = end_time

                delta_t = (end_time - start_time) / step_count
                settings.setdefault("solver_settings", {}).setdefault("time_stepping", {})["time_step"] = delta_t

                self._log(
                    f"Updated {stage_name}: start_time={start_time}, end_time={end_time}, time_step={delta_t}",
                    "info")
                start_time = end_time

            self.raw_text = json.dumps(data, indent=4)
            self._write_back()

        except Exception as e:
            raise RuntimeError(f"Failed to update staged timings: {e}") from e

    def append_stage(self, duration: float, steps: int):
        """
        Appends a new stage by copying the structure of the last existing stage.
        It automatically sets the correct start_time, end_time, and time_step.
        """
        data = self._load_json()

        stage_names = list(data["stages"].keys())

        last_stage_key = stage_names[-1]
        new_stage_index = len(stage_names) + 1
        new_stage_key = f"stage_{new_stage_index}"

        new_stage = json.loads(json.dumps(data["stages"][last_stage_key]))

        if "stage_preprocess" in new_stage:
            del new_stage["stage_preprocess"]

        previous_end_time = new_stage["stage_settings"]["problem_data"]["end_time"]

        new_stage["stage_settings"]["problem_data"]["start_time"] = previous_end_time
        new_stage["stage_settings"]["problem_data"]["end_time"] = previous_end_time + duration
        new_stage["stage_settings"]["solver_settings"]["time_stepping"]["time_step"] = duration / steps

        new_stage["stage_settings"]["output_processes"]["gid_output"][0]["Parameters"][
            "output_name"] = f"gid_output/output_stage{new_stage_index}"

        data["stages"][new_stage_key] = new_stage
        data["orchestrator"]["settings"]["execution_list"].append(new_stage_key)

        self.raw_text = json.dumps(data, indent=4)
        self._write_back()
        self._log(f"Appended a new stage: {new_stage_key}", "info")

    def update_top_displacement_table_numbers(self):
        """
        Updates the 'table' field in each stage for 'PorousDomain.top_displacement'
        so that its Y-direction (index 1) matches the stage number (starting from 1).
        Only applies for multi-stage tests.
        """
        try:
            data = self._load_json()
            stage_names = list(data["stages"].keys())

            for i, stage_name in enumerate(stage_names):
                stage = data["stages"][stage_name]
                table_index_list = [0, i + 1, 0]
                for process in stage.get("stage_settings", {}).get("processes", {}).get("constraints_process_list", []):
                    if (
                            process.get("python_module") == "apply_vector_constraint_table_process"
                            and process.get("Parameters", {}).get("model_part_name") == "PorousDomain.top_displacement"
                    ):
                        process["Parameters"]["table"] = table_index_list

            self.raw_text = json.dumps(data, indent=4)
            self._write_back()

        except Exception as e:
            self._log(f"[ERROR] Exception: {e}", "error")
            raise
