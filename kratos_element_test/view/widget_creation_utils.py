from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp


def create_entries(container, title, labels, units, defaults):
    """Create entry widgets in Kivy. Returns widgets dict and callbacks dict."""
    widgets = {}
    callbacks = {}
    
    if title:
        title_label = Label(
            text=title,
            size_hint_y=None,
            height=dp(30),
            bold=True,
            font_size='12sp'
        )
        container.add_widget(title_label)
    
    for i, label in enumerate(labels):
        unit = units[i] if i < len(units) else ""
        
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(5))
        
        label_widget = Label(
            text=label,
            size_hint_x=0.4,
            font_size='10sp'
        )
        row.add_widget(label_widget)
        
        entry = TextInput(
            text=str(defaults.get(label, "")),
            multiline=False,
            size_hint_x=0.4,
            font_size='10sp'
        )
        row.add_widget(entry)
        
        unit_label = Label(
            text=unit,
            size_hint_x=0.2,
            font_size='10sp'
        )
        row.add_widget(unit_label)
        
        container.add_widget(row)
        widgets[label] = entry
        
        # Create callback that can be bound to entry.text
        def make_callback(entry_widget, label_key):
            def callback(instance, value):
                # Placeholder for string_var behavior
                pass
            return callback
        
        callbacks[label] = make_callback(entry, label)
    
    return widgets, callbacks
