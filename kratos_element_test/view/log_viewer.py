import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
import tkinter as tk

from kratos_element_test.view.ui_constants import INPUT_SECTION_FONT
from kratos_element_test.view.ui_logger import init_log_widget


class LogViewer(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        ttk.Label(self, text="Log Output:", font=(INPUT_SECTION_FONT, 10, "bold")).pack(
            anchor="w"
        )
        self.log_widget_container = ScrolledText(
            self, height=6, width=40, wrap="word", autohide=True
        )
        self.log_widget_container.text.config(font=("Courier", 9))
        self.log_widget_container.pack(fill="x", expand=False)
        
        self.log_widget = self.log_widget_container.text

        self.log_widget.bind("<Key>", lambda e: "break")
        self.log_widget.bind("<Control-c>", lambda e: self._copy_selection())

        init_log_widget(self.log_widget)

    def _copy_selection(self):
        try:
            selection = self.log_widget.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(selection)
        except tk.TclError:
            pass
