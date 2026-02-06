"""
THALOS Prime - Advanced GUI Package
Advanced graphical user interface components.
"""

from typing import Dict, Any, Optional


class AdvancedGUIComponent:
    """Base class for advanced GUI components."""
    
    def __init__(self, name: str):
        self.name = name
        self.visible = True
        self.enabled = True
    
    def show(self) -> None:
        """Show the component."""
        self.visible = True
    
    def hide(self) -> None:
        """Hide the component."""
        self.visible = False
    
    def enable(self) -> None:
        """Enable the component."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the component."""
        self.enabled = False


class Window(AdvancedGUIComponent):
    """Window component."""
    
    def __init__(self, title: str = "THALOS Prime"):
        super().__init__('window')
        self.title = title
        self.width = 800
        self.height = 600
        self.children = []
    
    def add_child(self, component: AdvancedGUIComponent) -> None:
        """Add a child component."""
        self.children.append(component)


class Panel(AdvancedGUIComponent):
    """Panel component."""
    
    def __init__(self, name: str = 'panel'):
        super().__init__(name)
        self.background = '#ffffff'


class Button(AdvancedGUIComponent):
    """Button component."""
    
    def __init__(self, text: str = 'Button'):
        super().__init__('button')
        self.text = text
        self.on_click = None
    
    def click(self) -> None:
        """Trigger click event."""
        if self.on_click and self.enabled:
            self.on_click()


class TextInput(AdvancedGUIComponent):
    """Text input component."""
    
    def __init__(self, placeholder: str = ''):
        super().__init__('text_input')
        self.placeholder = placeholder
        self.value = ''
    
    def get_value(self) -> str:
        """Get input value."""
        return self.value
    
    def set_value(self, value: str) -> None:
        """Set input value."""
        self.value = value


# Export components
__all__ = [
    'AdvancedGUIComponent',
    'Window',
    'Panel',
    'Button',
    'TextInput',
]
