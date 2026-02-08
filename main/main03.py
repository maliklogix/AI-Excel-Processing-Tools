import os
import tkinter as tk
import ttkbootstrap as tb
from tkinter import filedialog, messagebox

from main.main02 import ExtendedApp, TOOL_DEFS  # Import base app + tools and existing tool definitions
from utils.combinations.file_combinations import FilesCombinationsTool

# -----------------------------
# Further Extended Application
# -----------------------------

class FurtherExtendedApp(ExtendedApp):
    def __init__(self, root):
        super().__init__(root)
        self.files_comb_tool = FilesCombinationsTool(root)
        
    # ---- Files Combinations Tool
    def action_files_combinations(self):
        self.files_comb_tool.open_tool_window()
    
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
        handlers['dummytool'] = self.action_dummy_tool
        handlers['filescombinations'] = self.action_files_combinations
        return handlers

# -----------------------------
# Add tool definitions
# -----------------------------

TOOL_DEFS.append({
    'key': 'dummytool',
    'title': 'Dummy Tool',
    'desc': 'A placeholder tool to demonstrate further extensibility.',
    'icon': '💡',
    'action_text': 'Open',
})

TOOL_DEFS.append({
    'key': 'filescombinations',
    'title': 'Files Combinations',
    'desc': 'Create combinations of records from CSV/Excel files with unique column values.',
    'icon': '📊',
    'action_text': 'Open Tool',
})

# -----------------------------
# Main execution
# -----------------------------

if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    root.title("Extended Data Processing Toolkit")
    root.geometry("1000x700")
    
    app = FurtherExtendedApp(root)
    app.pack(fill="both", expand=True)
    
    root.mainloop()