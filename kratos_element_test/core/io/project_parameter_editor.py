# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

import re
import json


def _fallback_log(msg: str, level: str = "info"):
    print(f"{level.upper()}: {msg}")

class ProjectParameterEditor:
    def __init__(self, json_path, logger=None):
        # logger :  Optional logger function to log messages.
        #    Callable with signature ``logger(message: str, level: str = 'info') -> None``.
        #    If not provided, a no-op logger is used.
        self.json_path = json_path
        self._log = logger or _fallback_log
        with open(self.json_path, 'r') as f:
            self.raw_text = f.read()

    def _write_back(self):
        with open(self.json_path, 'w') as f:
            f.write(self.raw_text)

    def update_nested_value(self, module_name, key, new_list) -> bool:
        try:
            data = json.loads(self.raw_text)

            loads_list = data.get("processes", {}).get("loads_process_list", [])
            for process in loads_list:
                if (process.get("python_module") == module_name
                    and key in process.get("Parameters", {})
                ):
                    process["Parameters"][key] = new_list
                    break
            else:
                self._log(f"Could not find '{key}' under '{module_name}'.", "warn")
                return False

            self.raw_text = json.dumps(data, indent=4)
            self._write_back()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to update '{key}' under '{module_name}': {e}") from e

    def update_property(self, property_name, new_value) -> int:
        pattern = rf'("{property_name}"\s*:\s*)([0-9eE+\.\-]+)'
        replacement = rf'\g<1>{new_value}'
        self.raw_text, count = re.subn(pattern, replacement, self.raw_text)
        if count == 0:
            self._log(f"Could not find '{property_name}' to update.", "warn")
        elif count > 1:
            self._log(f"Multiple occurrences of '{property_name}' found. Updated all {count}.", "warn")
        self._write_back()
        return count
