# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import re
import json
from kratos_element_test.core.core_utils import _fallback_log


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

    def update_stage_timings(self, end_times: list[float], step_counts: list[int]):
        """
        Applies staged start/end time logic. Assumes stage_1.start_time = 0.0.
        end_times: List of end_time values for each stage.
        num_steps: Number of steps (uniform across stages).
        """
        print(f"[DEBUG] update_stage_timings(): Received end_times = {end_times}")
        print(f"[DEBUG] update_stage_timings(): Received num_steps = {step_counts}")

        try:
            data = self._load_json()

            if "stages" not in data:
                self._log("update_stage_timings is only supported in orchestrator-based files.", "error")
                return

            stage_names = list(data["stages"].keys())
            if len(end_times) != len(stage_names):
                raise ValueError(f"Provided {len(end_times)} end_times but found {len(stage_names)} stages.")

            start_time = 0.0
            for i, stage_name in enumerate(stage_names):

                print(
                    f"Stage {stage_name}: start={start_time}, end={end_times[i]}, step={(end_times[i] - start_time) / step_counts[i]}")

                stage = data["stages"][stage_name]
                settings = stage.get("stage_settings", {})

                # Always set start_time based on previous end_time
                settings.setdefault("problem_data", {})["start_time"] = start_time
                settings["problem_data"]["end_time"] = end_times[i]

                delta_t = (end_times[i] - start_time) / step_counts[i]
                settings.setdefault("solver_settings", {}).setdefault("time_stepping", {})["time_step"] = delta_t

                self._log(
                    f"Updated {stage_name}: start_time={start_time}, end_time={end_times[i]}, time_step={delta_t}",
                    "info")
                start_time = end_times[i]

            self.raw_text = json.dumps(data, indent=4)
            self._write_back()

        except Exception as e:
            raise RuntimeError(f"Failed to update staged timings: {e}") from e

    def append_crs_stage(self, duration: float, steps: int):
        """
        Appends a new CRS stage by copying the structure of the last existing stage.
        It automatically sets the correct start_time, end_time, and time_step.
        """
        data = self._load_json()

        if "stages" not in data:
            self._log("append_crs_stage is only supported in orchestrator-based files.", "error")
            return

        stage_names = list(data["stages"].keys())
        if not stage_names:
            self._log("No existing stage to clone.", "error")
            return

        last_stage_key = stage_names[-1]
        new_stage_index = len(stage_names) + 1
        new_stage_key = f"stage_{new_stage_index}"

        # Clone the last stage
        new_stage = json.loads(json.dumps(data["stages"][last_stage_key]))  # deep copy

        # Set start_time, end_time, and time_step
        last_end_time = data["stages"][last_stage_key]["stage_settings"]["problem_data"]["end_time"]
        new_end_time = last_end_time + duration
        time_step = duration / steps

        new_stage["stage_settings"]["problem_data"]["start_time"] = last_end_time
        new_stage["stage_settings"]["problem_data"]["end_time"] = new_end_time
        new_stage["stage_settings"]["solver_settings"]["time_stepping"]["time_step"] = time_step

        # Update gid_output name to avoid overwriting
        new_stage["stage_settings"]["output_processes"]["gid_output"][0]["Parameters"][
            "output_name"] = f"gid_output/output_stage{new_stage_index}"

        data["stages"][new_stage_key] = new_stage
        data["orchestrator"]["settings"]["execution_list"].append(new_stage_key)

        self.raw_text = json.dumps(data, indent=4)
        self._write_back()
        self._log(f"Appended new CRS stage: {new_stage_key}", "info")
