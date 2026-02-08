import os
import tkinter as tk
import ttkbootstrap as tb
from tkinter import filedialog, messagebox

from main.main02 import ExtendedApp, TOOL_DEFS  # Import base app + tools and existing tool definitions
from utils.combinations.file_combinations import open_files_combinations_tool

# -----------------------------
# Further Extended Application
# -----------------------------
class FurtherExtendedApp(ExtendedApp):
    def __init__(self, root):
        super().__init__(root)

    # ---- Files Combinations Tool
    def action_files_combinations(self):
        open_files_combinations_tool(self.root)

    # ---- Dummy Tool
    def action_dummy_tool(self):
        win = tb.Toplevel(self.root)
        win.title("Dummy Tool")
        win.geometry("400x250")
        
        main_frame = tb.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tb.Label(main_frame, text="This is a Dummy Tool!", font=("Segoe UI", 14, "bold")).pack(pady=20)
        tb.Label(main_frame, text="It doesn't do much, but it shows how to extend the app.").pack(pady=10)

        def show_message():
            messagebox.showinfo("Dummy Action", "Dummy button pressed! Nothing really happens.")

        tb.Button(main_frame, text="Perform Dummy Action", bootstyle="primary", command=show_message).pack(pady=20)

    # ---- Extend handlers further
    def get_action_handlers(self):
        handlers = super().get_action_handlers()
        handlers['filescombinations'] = self.action_files_combinations
        handlers['dummytool'] = self.action_dummy_tool
        return handlers


# -----------------------------
# Add tool definition for Files Combinations
# -----------------------------
TOOL_DEFS.append({
    'key': 'filescombinations',
    'title': 'Files Combinations',
    'desc': 'Generate file subsets and combinations from master CSV/Excel.',
    'icon': '🗂️',
    'action_text': 'Open',
})

# -----------------------------
# Add tool definition for Dummy Tool
# -----------------------------
TOOL_DEFS.append({
    'key': 'dummytool',
    'title': 'Dummy Tool',
    'desc': 'A placeholder tool to demonstrate further extensibility.',
    'icon': '💡',
    'action_text': 'Open',
})
