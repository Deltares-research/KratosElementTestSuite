# Kivy Conversion Notes

## Overview
The GUI has been converted from ttkbootstrap/tkinter to Kivy. This is a proof-of-concept conversion.

## Key Changes

### Dependencies
- Replaced `ttkbootstrap` with `kivy` in `pyproject.toml`
- No garden package needed - using matplotlib's native backend

### Matplotlib Integration

Instead of using kivy.garden.matplotlib (which has installation issues), we use matplotlib's native AGG backend and convert to Kivy textures:

```python
from matplotlib.backends.backend_agg import FigureCanvasAgg
from kivy.graphics.texture import Texture

# Render to buffer
canvas = FigureCanvasAgg(fig)
canvas.draw()
buf = canvas.buffer_rgba()

# Create Kivy texture
texture = Texture.create(size=(w, h), colorfmt='rgba')
texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
```

This approach:
- No external dependencies beyond standard Kivy and matplotlib
- Works reliably across platforms
- Full matplotlib functionality

### Architecture Changes

#### Widget Mapping
- `ttk.Frame` → `BoxLayout`
- `ttk.Label` → `Label`
- `ttk.Entry` → `TextInput`
- `ttk.Button` → `Button`
- `ttk.Combobox` → `Spinner`
- `ScrolledText` → `ScrollView` + `TextInput`
- `tk.Canvas` + scrollbar → `ScrollView`

#### Layout System
- Replaced tkinter's pack/grid with Kivy's BoxLayout
- Using `size_hint` and `dp()` for responsive sizing
- Vertical/horizontal orientations via BoxLayout

#### Event Binding
- Changed from StringVar/trace to `.bind(text=callback)`
- Button callbacks use `on_press` instead of `command`
- Spinner selections use `.bind(text=callback)`

#### Application Structure
- MainUI now inherits from `kivy.app.App`
- Uses `build()` method instead of creating tkinter window
- Threading replaced with `Clock.schedule_once()` for UI updates

### Files Converted

1. **widget_creation_utils.py** - Entry widget creation with Kivy widgets
2. **ui_logger.py** - Logging adapted for Kivy TextInput
3. **log_viewer.py** - ScrollView + TextInput for log display
4. **soil_parameter_entries.py** - BoxLayout wrapper
5. **plot_viewer.py** - Native matplotlib to Kivy texture conversion
6. **soil_test_input_view.py** - Full conversion with image buttons, spinners, dynamic layouts
7. **ui_builder.py** - Main UI builder with ScrollView, BoxLayouts
8. **ui_menu.py** - App class with Popup for dialogs
9. **kratos_element_test_gui.py** - Updated entry point

### Limitations in POC

1. **File Dialogs**: Not implemented (would use `plyer.filechooser`)
2. **Menu Bar**: Not implemented (would use ActionBar or custom solution)
3. **License Dialog**: Basic Popup implementation
4. **Window Icon**: Not set (Kivy uses different approach)
5. **DPI Scaling**: Kivy handles automatically
6. **Some controller bindings**: May need adjustment for actual data flow

### Running the Application

```bash
# Install dependencies
poetry install

# Run the application
poetry run startElementTest
```

### Next Steps for Full Implementation

1. Implement file picker using `plyer` for DLL selection
2. Add proper menu bar (ActionBar or custom)
3. Implement export functionality
4. Test all controller bindings thoroughly
5. Add proper error handling and validation
6. Style widgets to match original theme
7. Add loading indicators during simulations
8. Test on different screen sizes/DPI

### Notes

- The conversion maintains the MVC pattern
- Controllers remain unchanged
- Model layer is untouched
- Only view layer converted to Kivy
- Thread-safe updates use Clock instead of tkinter's after()
- Matplotlib integration uses native AGG backend (no garden package needed)
