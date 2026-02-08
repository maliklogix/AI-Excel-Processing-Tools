# main.py
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Third-party UI theme
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Import the UI components
from ui.main_ui import create_main_ui, CardGrid

# -----------------------------
# Helpers: Safe/late imports of project modules
# -----------------------------
def _try_import(path, name):
    """Import a symbol (function/module) from a dotted path safely.
    path like "utils.converters", name like "csv_to_excel".
    Returns callable/module or raises helpful messagebox at call-time.
    """
    try:
        module = __import__(path, fromlist=[name])
        return getattr(module, name)
    except Exception as e:
        def _missing(*args, **kwargs):
            messagebox.showerror(
                "Missing dependency",
                f"Could not import {name} from {path}.\n\nError: {e}\n\n"
                "Make sure your project files are available or adjust TOOL_DEFS to your setup."
            )
        return _missing

# Lazily resolved callables (evaluated inside actions)
def get_utils():
    return {
        'csv_to_excel': _try_import('utils.converters', 'csv_to_excel'),
        'excel_to_csv': _try_import('utils.converters', 'excel_to_csv'),
        'merge_files': _try_import('utils.merger', 'merge_files'),
        'separate_by_column': _try_import('utils.separator', 'separate_by_column'),
        'run_step05_pipeline': _try_import('utils.ghl_compiler', 'run_step05_pipeline'),
        'run_column_mapper': _try_import('utils.column_mapper', 'run_column_mapper'),
        'run_script1': _try_import('utils.readRecords_campaignReady_driveReady', 'run_script1'),
        'run_script2': _try_import('utils.readRecords_campaignReady_driveReady', 'run_script2'),
        'run_script3': _try_import('utils.readRecords_campaignReady_driveReady', 'run_script3'),
        'process_directory': _try_import('pipeline.listbuilding_pipeline', 'process_directory'),
        'run_pipeline': _try_import('pipeline.listbuilding_pipeline', 'run_pipeline'),
        'process_aae_directory': _try_import('pipeline.AAE_3_phone_lsb', 'process_aae_directory'),
        'run_aae_pipeline': _try_import('pipeline.AAE_3_phone_lsb', 'run_aae_pipeline'),
    }

# -----------------------------
# Utility: loading popup
# -----------------------------
def show_loading(root, title="Processing..."):
    popup = tb.Toplevel(root)
    popup.title(title)
    popup.geometry("420x128")
    popup.resizable(False, False)
    popup.transient(root)
    popup.grab_set()

    popup.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() - popup.winfo_width()) // 2
    y = root.winfo_y() + (root.winfo_height() - popup.winfo_height()) // 2
    popup.geometry(f"+{x}+{y}")

    tb.Label(popup, text=title, font=("Segoe UI", 12, "bold")).pack(pady=10)
    prog = tb.Progressbar(popup, mode="indeterminate", bootstyle="success-striped")
    prog.pack(fill="x", padx=20, pady=10)
    prog.start(10)
    return popup, prog

def run_with_loader(root, func, *args, **kwargs):
    popup, prog = show_loading(root)

    def task():
        try:
            func(*args, **kwargs)
        finally:
            root.after(0, popup.destroy)

    threading.Thread(target=task, daemon=True).start()

# -----------------------------
# File/folder selectors
# -----------------------------
def select_files(filetypes):
    return filedialog.askopenfilenames(filetypes=filetypes)

def select_folder():
    return filedialog.askdirectory()

# -----------------------------
# Actions (each is self-contained and resilient to missing project files)
# -----------------------------
def action_csv_to_excel(root):
    U = get_utils()
    files = select_files([("CSV Files", "*.csv")])
    if not files:
        return
    out = select_folder()
    if not out:
        return

    def work():
        ok = 0
        for f in files:
            U['csv_to_excel'](f, out)
            ok += 1
        messagebox.showinfo("✅ Success", f"Converted {ok} CSV file(s) to Excel.")

    run_with_loader(root, work)

def action_excel_to_csv(root):
    U = get_utils()
    files = select_files([("Excel Files", "*.xlsx")])
    if not files:
        return
    out = os.path.join(os.getcwd(), "output", "csv")
    os.makedirs(out, exist_ok=True)

    def work():
        ok = 0
        for f in files:
            U['excel_to_csv'](f, out)
            ok += 1
        messagebox.showinfo("✅ Success", f"Converted {ok} Excel file(s) to CSV (folder: {out}).")

    run_with_loader(root, work)

def action_merge(root):
    U = get_utils()
    files = select_files([("Excel/CSV Files", "*.xlsx *.csv")])
    if not files:
        return

    def work():
        U['merge_files'](files)
        messagebox.showinfo("✅ Success", "Merged files into merged_output.xlsx")

    run_with_loader(root, work)

def action_separate(root):
    U = get_utils()
    file = filedialog.askopenfilename(filetypes=[("Excel/CSV Files", "*.xlsx *.csv")])
    if not file:
        return
    col = simpledialog.askstring("Column Name", "Enter column to split by:")
    if not col:
        return

    def work():
        U['separate_by_column'](file, col)
        messagebox.showinfo("✅ Success", f"Separated files by {col}")

    run_with_loader(root, work)

def action_ghl(root):
    U = get_utils()
    files = select_files([("Excel/CSV Files", "*.xlsx *.csv")])
    if not files:
        return

    def work():
        for f in files:
            U['run_step05_pipeline'](f)
        messagebox.showinfo("✅ Success", "GHL Ready files created")

    run_with_loader(root, work)

def action_column_mapper(root):
    U = get_utils()
    file = filedialog.askopenfilename(filetypes=[("Excel/CSV Files", "*.xlsx *.csv")])
    if file:
        U['run_column_mapper'](file)

# ---- Records Extractor (subwindow)
def action_records_extractor(root):
    U = get_utils()
    win = tb.Toplevel(root)
    win.title("Records Extractor Tool")
    win.geometry("520x420")
    win.configure(bg="#fff3e0")

    tb.Label(win, text="Select Folder to Process", font=("Segoe UI", 12, "bold"), background="#fff3e0").pack(pady=10)

    path_var = tk.StringVar()

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)

    frame_path = tb.Frame(win)
    frame_path.pack(pady=5)
    tb.Entry(frame_path, textvariable=path_var, width=42).pack(side="left", padx=5)
    tb.Button(frame_path, text="Browse", bootstyle="secondary", command=browse_folder).pack(side="left")

    tb.Label(win, text="Select Operation:", font=("Segoe UI", 10), background="#fff3e0").pack(pady=10)

    script_var = tk.StringVar(value="run_all")
    options_frame = tb.Frame(win, bootstyle="light")
    options_frame.pack(pady=5)

    tb.Radiobutton(options_frame, text="Run All Operations", variable=script_var, value="run_all", bootstyle="primary-toolbutton").pack(anchor="w", pady=5)
    tb.Radiobutton(options_frame, text="Extract Records from TXT/CSV", variable=script_var, value="script1", bootstyle="primary-toolbutton").pack(anchor="w", pady=5)
    tb.Radiobutton(options_frame, text="Collect GHL Ready Files & Create Zip", variable=script_var, value="script2", bootstyle="primary-toolbutton").pack(anchor="w", pady=5)
    tb.Radiobutton(options_frame, text="Organize Folders Structure", variable=script_var, value="script3", bootstyle="primary-toolbutton").pack(anchor="w", pady=5)

    def run_selected_script():
        folder = path_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("❌ Error", "Please select a valid folder path")
            return

        def work():
            original_dir = os.getcwd()
            os.chdir(folder)
            try:
                if script_var.get() == "script1":
                    U['run_script1']()
                    messagebox.showinfo("✅ Success", "Records extracted successfully!")
                elif script_var.get() == "script2":
                    U['run_script2']()
                    messagebox.showinfo("✅ Success", "GHL Ready files collected and zip created!")
                elif script_var.get() == "script3":
                    U['run_script3']()
                    messagebox.showinfo("✅ Success", "Folders organized successfully!")
                else:
                    U['run_script1'](); U['run_script2'](); U['run_script3']()
                    messagebox.showinfo("✅ Success", "All operations completed successfully!")
            except Exception as e:
                messagebox.showerror("❌ Error", f"An error occurred: {e}")
            finally:
                os.chdir(original_dir)

        run_with_loader(root, work)

    tb.Button(win, text="Run Selected Operation", bootstyle="success", command=run_selected_script, width=26).pack(pady=16)

# ---- Pipeline (bulk) subwindow
def action_pipeline_bulk(root):
    U = get_utils()
    win = tb.Toplevel(root)
    win.title("Pipeline ListBuilding Bulk")
    win.geometry("520x300")
    win.configure(bg="#fff3e0")

    tb.Label(win, text="Select Input Folder", font=("Segoe UI", 12, "bold"), background="#fff3e0").pack(pady=10)

    path_var = tk.StringVar()

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)

    frame_path = tb.Frame(win)
    frame_path.pack(pady=5)
    tb.Entry(frame_path, textvariable=path_var, width=42).pack(side="left", padx=5)
    tb.Button(frame_path, text="Browse", bootstyle="secondary", command=browse_folder).pack(side="left")

    step05_var = tk.BooleanVar(value=True)
    tb.Checkbutton(win, text="Include Step05 (GHL Ready)", variable=step05_var, bootstyle="round-toggle").pack(pady=14)

    def run_bulk():
        folder = path_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("❌ Error", "Please select a valid folder path")
            return

        def work():
            if not step05_var.get():
                import importlib
                pl = importlib.import_module('pipeline.listbuilding_pipeline')
                orig = getattr(pl, 'step_05_reshape', lambda df: df)
                setattr(pl, 'step_05_reshape', lambda df: df)
                U['process_directory'](folder)
                setattr(pl, 'step_05_reshape', orig)
            else:
                U['process_directory'](folder)
            messagebox.showinfo("✅ Done", "Pipeline processing complete.")

        run_with_loader(root, work)

    tb.Button(win, text="Run Pipeline", bootstyle="success", command=run_bulk, width=20).pack(pady=12)

# ---- AAE 3 Phone LSB subwindow
def action_aae_3_phone_lsb(root):
    U = get_utils()
    win = tb.Toplevel(root)
    win.title("AAE 3 Phone LSB")
    win.geometry("520x290")
    win.configure(bg="#fff3e0")

    tb.Label(win, text="Select Input Folder", font=("Segoe UI", 12, "bold"), background="#fff3e0").pack(pady=10)

    path_var = tk.StringVar()

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)

    frame_path = tb.Frame(win)
    frame_path.pack(pady=5)
    tb.Entry(frame_path, textvariable=path_var, width=42).pack(side="left", padx=5)
    tb.Button(frame_path, text="Browse", bootstyle="secondary", command=browse_folder).pack(side="left")

    step01_var = tk.BooleanVar(value=False)
    tb.Checkbutton(win, text="Process Step01 Files (Skip Step01 processing)", variable=step01_var, bootstyle="round-toggle").pack(pady=14)

    def run_aae():
        folder = path_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("❌ Error", "Please select a valid folder path")
            return

        def work():
            U['process_aae_directory'](folder, process_step01_files=step01_var.get())
            messagebox.showinfo("✅ Done", "AAE 3 Phone LSB processing complete.")

        run_with_loader(root, work)

    tb.Button(win, text="Run AAE 3 Phone LSB", bootstyle="success", command=run_aae, width=22).pack(pady=12)

# -----------------------------
# Tool definitions (add here; UI updates automatically)
# -----------------------------
def get_tool_defs(root):
    return [
        {
            'key': 'csv2xlsx',
            'title': 'CSV → Excel Converter',
            'desc': 'Convert one or more CSV files into XLSX format in a chosen folder.',
            'icon': '📄',
            'action_text': 'Convert',
            'command': lambda: action_csv_to_excel(root),
        },
        {
            'key': 'xlsx2csv',
            'title': 'Excel → CSV Converter',
            'desc': 'Export Excel workbooks as CSV files into an automatic output folder.',
            'icon': '📤',
            'action_text': 'Export',
            'command': lambda: action_excel_to_csv(root),
        },
        {
            'key': 'merge',
            'title': 'Merge CSV/Excel Files',
            'desc': 'Combine multiple CSV/XLSX files into a single merged workbook.',
            'icon': '🧩',
            'action_text': 'Merge',
            'command': lambda: action_merge(root),
        },
        {
            'key': 'separator',
            'title': 'File Separator (by Column)',
            'desc': 'Split a file into multiple files based on a column\'s unique values.',
            'icon': '✂️',
            'action_text': 'Separate',
            'command': lambda: action_separate(root),
        },
        {
            'key': 'ghl',
            'title': 'GHL Ready Compiler',
            'desc': 'Run Step05 pipeline to create GHL Ready files from your inputs.',
            'icon': '⚙️',
            'action_text': 'Compile',
            'command': lambda: action_ghl(root),
        },
        {
            'key': 'mapper',
            'title': 'Column Mapper Tool',
            'desc': 'Open the interactive mapper to align columns to your standard.',
            'icon': '🗺️',
            'action_text': 'Open',
            'command': lambda: action_column_mapper(root),
        },
        {
            'key': 'records',
            'title': 'Records Extractor Tool',
            'desc': 'Extract records, collect GHL files into zip, or organize folders.',
            'icon': '🔎',
            'action_text': 'Launch',
            'command': lambda: action_records_extractor(root),
        },
        {
            'key': 'pipeline',
            'title': 'MCHB MPV / 6 Phones LSB',
            'desc': 'Bulk list-building pipeline with optional Step05 reshaping.',
            'icon': '📦',
            'action_text': 'Run',
            'command': lambda: action_pipeline_bulk(root),
        },
        {
            'key': 'aae',
            'title': 'AAE 3 Phone LSB',
            'desc': 'Process AAE list-building with toggle for Step01 handling.',
            'icon': '📱',
            'action_text': 'Run',
            'command': lambda: action_aae_3_phone_lsb(root),
        },
        
    ]

# -----------------------------
# Main application entry point
# -----------------------------
if __name__ == "__main__":
    # Create the main window
    root = tb.Window(themename="cosmo")
    root.title("Hitrotech Data Tools")
    root.geometry("1050x760")
    root.minsize(880, 640)
    root.configure(bg="#FFE5B4")  # Light orange background
    
    # Get tool definitions
    tool_defs = get_tool_defs(root)
    
    # Create the UI
    create_main_ui(root, tool_defs)
    
    # Start the application
    root.mainloop()