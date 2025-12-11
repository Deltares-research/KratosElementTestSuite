# CustomTkinter Migration

This project has been migrated from standard tkinter to CustomTkinter for a modern, themed UI experience.

## Changes Made

### Dependencies
- Added `customtkinter >= 5.2.0` to `pyproject.toml`

### UI Files Updated

1. **ui_builder.py**
   - Replaced `tkinter.ttk` widgets with `customtkinter` equivalents
   - Changed `ttk.Frame` → `ctk.CTkFrame`
   - Changed `ttk.Label` → `ctk.CTkLabel`
   - Changed `ttk.Button` → `ctk.CTkButton`
   - Changed `ttk.Entry` → `ctk.CTkEntry`
   - Changed `ttk.Combobox` → `ctk.CTkComboBox`
   - Changed `ttk.Checkbutton` → `ctk.CTkCheckBox`
   - Replaced manual scrolling with `CTkScrollableFrame`
   - Updated image handling to use `CTkImage` for button images
   - Updated event bindings (ComboBox uses `command` instead of `bind`)

2. **ui_menu.py**
   - Changed root window from `tk.Tk()` → `ctk.CTk()`
   - Changed `tk.Toplevel()` → `ctk.CTkToplevel()`
   - Replaced `ttk.Frame` with `ctk.CTkFrame`
   - Updated all buttons and labels to use CustomTkinter widgets
   - Added appearance mode configuration (`ctk.set_appearance_mode("System")`)
   - Added color theme configuration (`ctk.set_default_color_theme("blue")`)
   - Updated scaling to use `ctk.set_widget_scaling()`

### Key Differences

#### Event Handling
- **Old (ttk.Combobox)**: `combobox.bind("<<ComboboxSelected>>", callback)`
- **New (CTkComboBox)**: `combobox.configure(command=callback)` where callback receives the selected value

#### Styling
- CustomTkinter automatically handles modern theming
- Removed manual relief/border configurations as CTk handles these automatically
- Button states use `fg_color` parameter for visual feedback

#### Scrolling
- Replaced manual Canvas + Scrollbar implementation with `CTkScrollableFrame`
- Simplified scrolling logic (handled automatically by CTk)

## Installation

To use the updated UI, install CustomTkinter:

```bash
pip install customtkinter
# or
poetry install
```

## Appearance Customization

You can customize the appearance by modifying the settings in `ui_menu.py`:

```python
# Change appearance mode: "System", "Dark", "Light"
ctk.set_appearance_mode("System")

# Change color theme: "blue", "green", "dark-blue"
ctk.set_default_color_theme("blue")
```

## Benefits

1. **Modern Look**: Automatic dark/light mode support
2. **Better Scaling**: Improved DPI scaling on high-resolution displays
3. **Consistent UI**: Cross-platform consistency in appearance
4. **Simplified Code**: Built-in scrollable frames and better widget management
5. **Active Development**: CustomTkinter is actively maintained with regular updates

## Compatibility

- Python 3.10+
- Windows, macOS, Linux
- All existing functionality preserved
