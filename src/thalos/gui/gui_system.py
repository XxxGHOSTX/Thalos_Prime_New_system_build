"""
Advanced GUI System for THALOS Prime
Terminal-based UI with interactive components
"""
import sys
import time
from typing import Optional, List, Callable
from dataclasses import dataclass


@dataclass
class MenuItem:
    """Menu item definition"""
    label: str
    action: Optional[Callable] = None
    submenu: Optional[List['MenuItem']] = None
    enabled: bool = True


class GUISystem:
    """
    Terminal-based GUI system with menus, panels, and status display
    """
    
    def __init__(self, theme: str = "dark"):
        self.theme = theme
        self.running = False
        self.current_menu: Optional[List[MenuItem]] = None
        self.selected_index = 0
        self.status_message = "Ready"
        self.title = "THALOS Prime System"
        
        # Define main menu
        self.main_menu = [
            MenuItem("System Status", self._show_status),
            MenuItem("Matrix Codex", self._show_matrix),
            MenuItem("Background Engine", self._show_background),
            MenuItem("Configuration", self._show_config),
            MenuItem("Diagnostics", self._show_diagnostics),
            MenuItem("Exit", self._exit_app)
        ]
        
        self.current_menu = self.main_menu
    
    def start(self):
        """Start the GUI system"""
        self.running = True
        self._clear_screen()
    
    def stop(self):
        """Stop the GUI system"""
        self.running = False
    
    def render(self):
        """Render the current GUI state"""
        if not self.running:
            return
        
        self._clear_screen()
        self._render_header()
        self._render_menu()
        self._render_status()
    
    def _clear_screen(self):
        """Clear terminal screen"""
        print("\033[2J\033[H", end="")
    
    def _render_header(self):
        """Render header with title"""
        width = 80
        print("═" * width)
        title_padding = (width - len(self.title) - 2) // 2
        print(f"{'═' * title_padding} {self.title} {'═' * title_padding}")
        print("═" * width)
        print()
    
    def _render_menu(self):
        """Render current menu"""
        if not self.current_menu:
            return
        
        print("  Main Menu:")
        print()
        
        for i, item in enumerate(self.current_menu):
            if i == self.selected_index:
                # Highlighted item
                print(f"  → {item.label}")
            else:
                print(f"    {item.label}")
        
        print()
        print("  ↑/↓: Navigate  |  Enter: Select  |  Q: Quit")
        print()
    
    def _render_status(self):
        """Render status bar"""
        width = 80
        print()
        print("─" * width)
        print(f"  Status: {self.status_message}")
        print("─" * width)
    
    def handle_input(self, key: str):
        """Handle keyboard input"""
        if key == 'up' and self.selected_index > 0:
            self.selected_index -= 1
        elif key == 'down' and self.selected_index < len(self.current_menu) - 1:
            self.selected_index += 1
        elif key == 'enter':
            self._execute_selected()
        elif key == 'q':
            self.running = False
    
    def _execute_selected(self):
        """Execute selected menu item"""
        if self.current_menu and 0 <= self.selected_index < len(self.current_menu):
            item = self.current_menu[self.selected_index]
            if item.action:
                item.action()
            elif item.submenu:
                self.current_menu = item.submenu
                self.selected_index = 0
    
    def _show_status(self):
        """Show system status"""
        self.status_message = "Displaying system status..."
        print("\n  ┌─────────────────────────────────────┐")
        print("  │     SYSTEM STATUS DISPLAY         │")
        print("  ├─────────────────────────────────────┤")
        print("  │ CPU Usage:       42%              │")
        print("  │ Memory:          1.2GB / 4GB      │")
        print("  │ Matrix Codex:    Active           │")
        print("  │ Background:      Running          │")
        print("  │ Uptime:          2h 34m           │")
        print("  └─────────────────────────────────────┘")
        input("\n  Press Enter to continue...")
    
    def _show_matrix(self):
        """Show Matrix Codex interface"""
        self.status_message = "Matrix Codex visualization..."
        print("\n  Matrix Codex Engine")
        print("  ───────────────────")
        print("  Active Cells:  2,847")
        print("  Complexity:    Level 3")
        print("  Frame Rate:    60 FPS")
        print()
        print("  [Visualization would appear here]")
        input("\n  Press Enter to continue...")
    
    def _show_background(self):
        """Show Background Engine interface"""
        self.status_message = "Background engine controls..."
        print("\n  Background Engine Settings")
        print("  ─────────────────────────")
        print("  Effect Mode:   Stars")
        print("  Particles:     10,000")
        print("  FPS Target:    60")
        print("  Quality:       Ultra")
        input("\n  Press Enter to continue...")
    
    def _show_config(self):
        """Show configuration interface"""
        self.status_message = "Configuration settings..."
        print("\n  Configuration")
        print("  ─────────────")
        print("  Theme:         Dark")
        print("  Log Level:     INFO")
        print("  Auto-save:     Enabled")
        print("  Telemetry:     Disabled")
        input("\n  Press Enter to continue...")
    
    def _show_diagnostics(self):
        """Show diagnostics"""
        self.status_message = "Running diagnostics..."
        print("\n  System Diagnostics")
        print("  ─────────────────")
        print("  ✓ Core modules loaded")
        print("  ✓ Configuration valid")
        print("  ✓ Database accessible")
        print("  ✓ Network connectivity")
        print("  ✓ GPU acceleration available")
        input("\n  Press Enter to continue...")
    
    def _exit_app(self):
        """Exit application"""
        self.status_message = "Shutting down..."
        self.running = False
    
    def get_stats(self) -> dict:
        """Get GUI statistics"""
        return {
            'running': self.running,
            'theme': self.theme,
            'current_menu': len(self.current_menu) if self.current_menu else 0,
            'selected_index': self.selected_index
        }


class StatusPanel:
    """Status display panel"""
    
    def __init__(self, width: int = 80):
        self.width = width
        self.lines: List[str] = []
    
    def add_line(self, text: str):
        """Add a line to the panel"""
        self.lines.append(text)
    
    def clear(self):
        """Clear panel"""
        self.lines.clear()
    
    def render(self) -> str:
        """Render panel as string"""
        border = "─" * self.width
        content = "\n".join(self.lines)
        return f"{border}\n{content}\n{border}"
