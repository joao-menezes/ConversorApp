import customtkinter as ctk
from typing import Optional

class ToolTipService:
    def __init__(self, widget: ctk.CTkBaseClass, text: str):
        self.widget = widget
        self.text = text
        self.tooltip: Optional[ctk.CTkToplevel] = None
        self._setup_bindings()

    def _setup_bindings(self) -> None:
        self.widget.bind("<Enter>", self._show_tooltip)
        self.widget.bind("<Leave>", self._hide_tooltip)

    def _show_tooltip(self, event=None) -> None:
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25

        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(self.tooltip, text=self.text)
        label.pack()

    def _hide_tooltip(self, event=None) -> None:
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None