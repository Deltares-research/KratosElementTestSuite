from tkinter import ttk
import tkinter.font as tkFont


def create_entries(frame, title, labels, units, defaults):
    widgets = {}
    string_vars = {}
    default_font = tkFont.nametofont("TkDefaultFont").copy()
    default_font.configure(size=10)

    ttk.Label(frame, text=title, font=("Arial", 12, "bold")).pack(
        anchor="w", padx=5, pady=5
    )
    for i, label in enumerate(labels):
        string_var = tk.StringVar()
        string_var.set(defaults.get(label, ""))
        unit = units[i] if i < len(units) else ""
        row = ttk.Frame(frame)
        row.pack(fill="x", padx=10, pady=2)
        ttk.Label(row, text=label, font=default_font).pack(side="left", padx=5)
        entry = ttk.Entry(row, font=default_font, width=20, textvariable=string_var)
        entry.pack(side="left", fill="x", expand=True)
        ttk.Label(row, text=unit, font=default_font).pack(side="left", padx=5)
        widgets[label] = entry
        string_vars[label] = string_var
    return widgets, string_vars
