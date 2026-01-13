# ©Deltares 2025
# This is a prototype version
# Contact kratos@deltares.nl

_log_widget = None

def init_log_widget(widget):
    global _log_widget
    _log_widget = widget

def log_message(msg, level="info"):
    if _log_widget is None:
        print(f"{level.upper()}: {msg}")
        return

    prefix = {"info": "[INFO]", "error": "[ERROR]", "warn": "[WARN]"}
    message = f"{prefix.get(level, '[INFO]')} {msg}\n"
    _log_widget.text += message
    # Scroll to end by setting cursor position
    _log_widget.cursor = (0, len(_log_widget.text))

def clear_log():
    if _log_widget is not None:
        _log_widget.text = ""
