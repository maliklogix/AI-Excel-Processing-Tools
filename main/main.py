import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Third-party UI theme
import ttkbootstrap as tb
import ttkbootstrap as tb
from tkinter import filedialog, ttk

from ttkbootstrap.constants import *

from ui.ui_main import HitrotechUI
from utils.merger import open_merger_tool

import importlib
import importlib.util
import pandas as pd
from datetime import datetime

# -----------------------------
# Helpers: Safe/late imports of project modules (keeps this file standalone)
# -----------------------------
def _try_import(path, name):
    """
    Import a symbol (function/module) from a dotted path safely.
    path like "utils.converters", name like "csv_to_excel".
    If normal import fails (e.g. module filename starts with digit), try loading by file path.
    Returns callable/module or returns a function that raises a messagebox on call.
    """
    try:
        module = __import__(path, fromlist=[name])
        return getattr(module, name)
    except Exception as e:
        # Try file-based import fallback (useful when filename/module name starts with digit)
        try:
            # Convert dotted path to a filepath relative to project cwd
            file_path = os.path.join(os.getcwd(), *path.split('.')) + '.py'
            if os.path.exists(file_path):
                spec = importlib.util.spec_from_file_location(path, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return getattr(module, name)
        except Exception:
            pass

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
        'run_column_adder': _try_import('utils.gen_coloumns_adder', 'run_column_adder'),
        'run_record_collector': _try_import('utils.record_collector', 'run_record_collector'),
        # Vacant lot 6 phone pipeline (module filename may start with digit; fallback loader will handle it)
        'run_vacant_6_pipeline': _try_import('pipeline.vacant_lot_pipeline.6_phone_number_vacant_lot', 'run_pipeline'),
    }

# -----------------------------


# Application logic
# -----------------------------
class HitrotechApp:

    def __init__(self, root):
        self.root = root
        self.utils = get_utils()
        self.ui = None
        self.setup_app()

    # ///////////// Always on TOP
    def open_tool_window(self, tool_func):
        win = tk.Toplevel(self.root)
        win.attributes("-topmost", True)
        tool_func(win, self.ui)
        return win
    # /////////////

    def action_record_collector(self):
        win = tb.Toplevel(self.root)
        win.title("Record Collector Tool")
        win.geometry("520x420")
        
        # Use ttkbootstrap style instead of bg color
        main_frame = tb.Frame(win)
        main_frame.pack(fill="both", expand=True)

        tb.Label(main_frame, text="Select Base Directory", font=("Segoe UI", 12, "bold")).pack(pady=10)

        path_var = tk.StringVar()

        def browse_folder():
            folder = filedialog.askdirectory()
            if folder:
                path_var.set(folder)

        frame_path = tb.Frame(main_frame)
        frame_path.pack(pady=5)
        tb.Entry(frame_path, textvariable=path_var, width=42).pack(side="left", padx=5)
        tb.Button(frame_path, text="Browse", bootstyle="secondary", command=browse_folder).pack(side="left")

        tb.Label(main_frame, text="Select Folder Type:", font=("Segoe UI", 10)).pack(pady=10)

        predefined = ["GHL Ready", "SkipTraced", "2BSkip", "CC Ready", "No Hit", "SC Ready"]
        folder_var = tk.StringVar(value=predefined[0])

        folder_menu = tb.Combobox(main_frame, textvariable=folder_var, values=predefined, width=40)
        folder_menu.pack(pady=5)

        tb.Label(main_frame, text="Or enter custom folder name:", font=("Segoe UI", 10)).pack(pady=6)
        custom_var = tk.StringVar()
        tb.Entry(main_frame, textvariable=custom_var, width=42).pack(pady=5)

        def run_collector():
            base = path_var.get().strip()
            if not base or not os.path.isdir(base):
                self.ui.show_error("❌ Error", "Please select a valid base folder")
                return

            folder_name = custom_var.get().strip() or folder_var.get()
            if not folder_name:
                self.ui.show_error("❌ Error", "Please select or enter a folder name")
                return

            def work():
                self.utils['run_record_collector'](base, folder_name)
                self.ui.show_info("✅ Done", f"Files collected for '{folder_name}'")

            self.run_with_loader(work)

        tb.Button(main_frame, text="Run Collector", bootstyle="success", command=run_collector, width=22).pack(pady=14)

    def setup_app(self):
        # Create UI with tool definitions and action handlers
        self.ui = HitrotechUI(self.root, TOOL_DEFS, self.get_action_handlers())

    def get_action_handlers(self):
        return {
            'recordcollector': self.action_record_collector,
            'csv2xlsx': self.action_csv_to_excel,
            'xlsx2csv': self.action_excel_to_csv,
            'merge': self.action_merge,
            'separator': self.action_separate,
            'ghl': self.action_ghl,
            'mapper': self.action_column_mapper,
            'records': self.action_records_extractor,
            'pipeline': self.action_pipeline_bulk,
            'aae': self.action_aae_3_phone_lsb,
            'coladder': self.action_column_adder,
            # new vacant lot 6 phones tool
            'vacant6': self.action_vacant_lot_6_phone,
        }

    def run_with_loader(self, func, *args, **kwargs):
        popup, prog = self.ui.show_loading()

        def task():
            try:
                func(*args, **kwargs)
            finally:
                # destroy the loader on the GUI thread
                self.root.after(0, popup.destroy)

        threading.Thread(target=task, daemon=True).start()

    # -----------------------------
    # Actions (each is self-contained and resilient to missing project files)
    # -----------------------------
    def action_csv_to_excel(self):
        files = self.ui.select_files([("CSV Files", "*.csv")])
        if not files:
            return
        out = self.ui.select_folder()
        if not out:
            return

        def work():
            ok = 0
            for f in files:
                self.utils['csv_to_excel'](f, out)
                ok += 1
            self.ui.show_info("✅ Success", f"Converted {ok} CSV file(s) to Excel.")

        self.run_with_loader(work)

    def action_excel_to_csv(self):
        files = self.ui.select_files([("Excel Files", "*.xlsx")])
        if not files:
            return
        out = os.path.join(os.getcwd(), "output", "csv")
        os.makedirs(out, exist_ok=True)

        def work():
            ok = 0
            for f in files:
                self.utils['excel_to_csv'](f, out)
                ok += 1
            self.ui.show_info("✅ Success", f"Converted {ok} Excel file(s) to CSV (folder: {out}).")

        self.run_with_loader(work)

    def action_merge(self):
        open_merger_tool(self.root, self.ui)

    def action_separate(self):
        # Create advanced separator dashboard
        self._create_separator_dashboard()

    def _create_separator_dashboard(self):
        """Create an advanced dashboard for file separation with multiple options"""
        win = tb.Toplevel(self.root)
        win.title("Advanced File Separator")
        win.geometry("900x700")
        
        # Main container with scrollbar
        container = tb.Frame(win, bootstyle="light")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # File selection section
        file_frame = tb.LabelFrame(scrollable_frame, text="File Selection", bootstyle="info")
        file_frame.pack(fill="x", padx=10, pady=10)
        
        tb.Label(file_frame, text="Select multiple files to separate by column values", 
                font=("Segoe UI", 10)).pack(pady=5)
        
        # File listbox with scrollbar
        file_list_frame = tb.Frame(file_frame)
        file_list_frame.pack(fill="x", padx=10, pady=5)
        
        file_listbox = tk.Listbox(file_list_frame, height=8, selectmode=tk.EXTENDED)
        file_scrollbar = ttk.Scrollbar(file_list_frame, orient="vertical", command=file_listbox.yview)
        file_listbox.configure(yscrollcommand=file_scrollbar.set)
        
        file_listbox.pack(side="left", fill="both", expand=True)
        file_scrollbar.pack(side="right", fill="y")
        
        # File buttons
        file_btn_frame = tb.Frame(file_frame)
        file_btn_frame.pack(fill="x", padx=10, pady=5)
        
        def add_files():
            files = filedialog.askopenfilenames(
                filetypes=[("Excel/CSV Files", "*.xlsx *.csv"), ("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]
            )
            for file in files:
                if file not in file_listbox.get(0, tk.END):
                    file_listbox.insert(tk.END, file)
            update_column_dropdowns()
        
        def remove_files():
            selected = file_listbox.curselection()
            for index in selected[::-1]:
                file_listbox.delete(index)
            update_column_dropdowns()
        
        def clear_files():
            file_listbox.delete(0, tk.END)
            update_column_dropdowns()
        
        tb.Button(file_btn_frame, text="Add Files", bootstyle="secondary", 
                 command=add_files).pack(side="left", padx=5)
        tb.Button(file_btn_frame, text="Remove Selected", bootstyle="danger", 
                 command=remove_files).pack(side="left", padx=5)
        tb.Button(file_btn_frame, text="Clear All", bootstyle="warning", 
                 command=clear_files).pack(side="left", padx=5)
        
        # Column selection section
        column_frame = tb.LabelFrame(scrollable_frame, text="Column Selection", bootstyle="primary")
        column_frame.pack(fill="x", padx=10, pady=10)
        
        tb.Label(column_frame, text="Select column to separate by:", 
                font=("Segoe UI", 10)).pack(pady=5)
        
        column_var = tk.StringVar()
        column_dropdown = tb.Combobox(column_frame, textvariable=column_var, width=40)
        column_dropdown.pack(pady=5)
        
        # Options section
        options_frame = tb.LabelFrame(scrollable_frame, text="Separation Options", bootstyle="success")
        options_frame.pack(fill="x", padx=10, pady=10)
        
        # Output format
        format_frame = tb.Frame(options_frame)
        format_frame.pack(fill="x", padx=10, pady=5)
        tb.Label(format_frame, text="Output Format:").pack(side="left")
        format_var = tk.StringVar(value="xlsx")
        tb.Radiobutton(format_frame, text="Excel", variable=format_var, 
                      value="xlsx", bootstyle="success").pack(side="left", padx=10)
        tb.Radiobutton(format_frame, text="CSV", variable=format_var, 
                      value="csv", bootstyle="success").pack(side="left", padx=10)
        tb.Radiobutton(format_frame, text="Both", variable=format_var, 
                      value="both", bootstyle="success").pack(side="left", padx=10)
        
        # NaN handling
        nan_frame = tb.Frame(options_frame)
        nan_frame.pack(fill="x", padx=10, pady=5)
        tb.Label(nan_frame, text="Handle NaN Values:").pack(side="left")
        nan_var = tk.StringVar(value="skip")
        tb.Radiobutton(nan_frame, text="Skip", variable=nan_var, 
                      value="skip", bootstyle="info").pack(side="left", padx=10)
        tb.Radiobutton(nan_frame, text="Include as 'Unknown'", variable=nan_var, 
                      value="include", bootstyle="info").pack(side="left", padx=10)
        tb.Radiobutton(nan_frame, text="Separate File", variable=nan_var, 
                      value="separate", bootstyle="info").pack(side="left", padx=10)
        
        # File limit
        limit_frame = tb.Frame(options_frame)
        limit_frame.pack(fill="x", padx=10, pady=5)
        tb.Label(limit_frame, text="Max Files to Create (0 = unlimited):").pack(side="left")
        limit_var = tk.IntVar(value=0)
        tb.Spinbox(limit_frame, from_=0, to=1000, textvariable=limit_var, 
                  width=10).pack(side="left", padx=10)
        
        # Output location
        output_frame = tb.LabelFrame(scrollable_frame, text="Output Location", bootstyle="warning")
        output_frame.pack(fill="x", padx=10, pady=10)
        
        output_var = tk.StringVar(value=os.path.join(os.getcwd(), "output", "separated"))
        
        def browse_output():
            folder = filedialog.askdirectory()
            if folder:
                output_var.set(folder)
        
        output_btn_frame = tb.Frame(output_frame)
        output_btn_frame.pack(fill="x", padx=10, pady=5)
        tb.Label(output_btn_frame, text="Output Folder:").pack(side="left")
        tb.Entry(output_btn_frame, textvariable=output_var, width=50).pack(side="left", padx=10)
        tb.Button(output_btn_frame, text="Browse", bootstyle="secondary", 
                 command=browse_output).pack(side="left")
        
        # Progress section
        progress_frame = tb.LabelFrame(scrollable_frame, text="Progress", bootstyle="dark")
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = tb.Progressbar(progress_frame, variable=progress_var, 
                                     maximum=100, bootstyle="success-striped")
        progress_bar.pack(fill="x", padx=10, pady=5)
        
        status_var = tk.StringVar(value="Ready")
        status_label = tb.Label(progress_frame, textvariable=status_var, 
                               font=("Segoe UI", 9))
        status_label.pack(pady=5)
        
        # Action buttons
        action_frame = tb.Frame(scrollable_frame)
        action_frame.pack(pady=10)
        
        def update_column_dropdowns():
            """Update the column dropdown with columns from the first selected file"""
            files = file_listbox.get(0, tk.END)
            if files:
                try:
                    first_file = files[0]
                    if first_file.endswith('.csv'):
                        df = pd.read_csv(first_file, nrows=1)
                    else:
                        df = pd.read_excel(first_file, nrows=1)
                    
                    columns = list(df.columns)
                    column_dropdown['values'] = columns
                    if columns:
                        column_var.set(columns[0])
                except Exception as e:
                    messagebox.showerror("Error", f"Could not read file: {e}")
        
        def run_separation():
            files = file_listbox.get(0, tk.END)
            if not files:
                messagebox.showerror("Error", "Please select at least one file")
                return
            
            column = column_var.get()
            if not column:
                messagebox.showerror("Error", "Please select a column to separate by")
                return
            
            output_folder = output_var.get()
            if not output_folder:
                messagebox.showerror("Error", "Please select an output folder")
                return
            
            os.makedirs(output_folder, exist_ok=True)
            
            def process_files():
                total_files = len(files)
                processed = 0
                
                for file in files:
                    try:
                        status_var.set(f"Processing {os.path.basename(file)}...")
                        progress_var.set((processed / total_files) * 100)
                        
                        # Use the advanced separator function
                        self.utils['separate_by_column'](
                            file=file,
                            column=column,
                            output_dir=os.path.join(output_folder, os.path.splitext(os.path.basename(file))[0]),
                            file_format=format_var.get(),
                            handle_na=nan_var.get(),
                            max_files=limit_var.get() if limit_var.get() > 0 else None
                        )
                        
                        processed += 1
                        progress_var.set((processed / total_files) * 100)
                        
                    except Exception as e:
                        self.root.after(0, lambda: messagebox.showerror(
                            "Error", f"Failed to process {file}: {str(e)}"))
                
                status_var.set("Complete!")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", f"Processed {processed} of {total_files} files"))
            
            # Run in background thread
            threading.Thread(target=process_files, daemon=True).start()
        
        tb.Button(action_frame, text="🔄 Update Columns", bootstyle="info", 
                 command=update_column_dropdowns).pack(side="left", padx=5)
        tb.Button(action_frame, text="➖ Separate Files", bootstyle="success", 
                 command=run_separation, width=20).pack(side="left", padx=5)
        
        # Initialize
        update_column_dropdowns()

    def action_column_adder(self):
        # Call the function from gen_coloumns_adder
        self.utils['run_column_adder'](self.root)

    def action_ghl(self):
        files = self.ui.select_files([("Excel/CSV Files", "*.xlsx *.csv")])
        if not files:
            return

        def work():
            for f in files:
                self.utils['run_step05_pipeline'](f)
            self.ui.show_info("✅ Success", "GHL Ready files created")

        self.run_with_loader(work)

    def action_column_mapper(self):
        file = filedialog.askopenfilename(filetypes=[("Excel/CSV Files", "*.xlsx *.csv")])
        if file:
            self.utils['run_column_mapper'](file)

    # ---- Records Extractor (subwindow)
    def action_records_extractor(self):
        win = tb.Toplevel(self.root)
        win.title("Records Extractor Tool")
        win.geometry("520x420")
        
        main_frame = tb.Frame(win)
        main_frame.pack(fill="both", expand=True)

        tb.Label(main_frame, text="Select Folder to Process", font=("Segoe UI", 12, "bold")).pack(pady=10)

        path_var = tk.StringVar()

        def browse_folder():
            folder = filedialog.askdirectory()
            if folder:
                path_var.set(folder)

        frame_path = tb.Frame(main_frame)
        frame_path.pack(pady=5)
        tb.Entry(frame_path, textvariable=path_var, width=42).pack(side="left", padx=5)
        tb.Button(frame_path, text="Browse", bootstyle="secondary", command=browse_folder).pack(side="left")

        tb.Label(main_frame, text="Select Operation:", font=("Segoe UI", 10)).pack(pady=10)

        script_var = tk.StringVar(value="run_all")
        options_frame = tb.Frame(main_frame, bootstyle="light")
        options_frame.pack(pady=5)

        tb.Radiobutton(options_frame, text="Run All Operations", variable=script_var, value="run_all", bootstyle="primary-toolbutton").pack(anchor="w", pady=5)
        tb.Radiobutton(options_frame, text="Extract Records from TXT/CSV", variable=script_var, value="script1", bootstyle="primary-toolbutton").pack(anchor="w", pady=5)
        tb.Radiobutton(options_frame, text="Collect GHL Ready Files & Create Zip", variable=script_var, value="script2", bootstyle="primary-toolbutton").pack(anchor="w", pady=5)
        tb.Radiobutton(options_frame, text="Organize Folders Structure", variable=script_var, value="script3", bootstyle="primary-toolbutton").pack(anchor="w", pady=5)

        def run_selected_script():
            folder = path_var.get().strip()
            if not folder or not os.path.isdir(folder):
                self.ui.show_error("❌ Error", "Please select a valid folder path")
                return

            def work():
                original_dir = os.getcwd()
                os.chdir(folder)
                try:
                    if script_var.get() == "script1":
                        self.utils['run_script1']()
                        self.ui.show_info("✅ Success", "Records extracted successfully!")
                    elif script_var.get() == "script2":
                        self.utils['run_script2']()
                        self.ui.show_info("✅ Success", "GHL Ready files collected and zip created!")
                    elif script_var.get() == "script3":
                        self.utils['run_script3']()
                        self.ui.show_info("✅ Success", "Folders organized successfully!")
                    else:
                        self.utils['run_script1'](); self.utils['run_script2'](); self.utils['run_script3']()
                        self.ui.show_info("✅ Success", "All operations completed successfully!")
                except Exception as e:
                    self.ui.show_error("❌ Error", f"An error occurred: {e}")
                finally:
                    os.chdir(original_dir)

            self.run_with_loader(work)

        tb.Button(main_frame, text="Run Selected Operation", bootstyle="success", command=run_selected_script, width=26).pack(pady=16)

    # ---- Pipeline (bulk) subwindow
    def action_pipeline_bulk(self):
        win = tb.Toplevel(self.root)
        win.title("Pipeline ListBuilding Bulk")
        win.geometry("520x300")
        
        main_frame = tb.Frame(win)
        main_frame.pack(fill="both", expand=True)

        tb.Label(main_frame, text="Select Input Folder", font=("Segoe UI", 12, "bold")).pack(pady=10)

        path_var = tk.StringVar()

        def browse_folder():
            folder = filedialog.askdirectory()
            if folder:
                path_var.set(folder)

        frame_path = tb.Frame(main_frame)
        frame_path.pack(pady=5)
        tb.Entry(frame_path, textvariable=path_var, width=42).pack(side="left", padx=5)
        tb.Button(frame_path, text="Browse", bootstyle="secondary", command=browse_folder).pack(side="left")

        step05_var = tk.BooleanVar(value=True)
        tb.Checkbutton(main_frame, text="Include Step05 (GHL Ready)", variable=step05_var, bootstyle="round-toggle").pack(pady=14)

        def run_bulk():
            folder = path_var.get().strip()
            if not folder or not os.path.isdir(folder):
                self.ui.show_error("❌ Error", "Please select a valid folder path")
                return

            def work():
                if not step05_var.get():
                    pl = importlib.import_module('pipeline.listbuilding_pipeline')
                    orig = getattr(pl, 'step_05_reshape', lambda df: df)
                    setattr(pl, 'step_05_reshape', lambda df: df)
                    self.utils['process_directory'](folder)
                    setattr(pl, 'step_05_reshape', orig)
                else:
                    self.utils['process_directory'](folder)
                self.ui.show_info("✅ Done", "Pipeline processing complete.")

            self.run_with_loader(work)

        tb.Button(main_frame, text="Run Pipeline", bootstyle="success", command=run_bulk, width=20).pack(pady=12)

    # ---- AAE 3 Phone LSB subwindow
    def action_aae_3_phone_lsb(self):
        win = tb.Toplevel(self.root)
        win.title("AAE 3 Phone LSB")
        win.geometry("520x290")
        
        main_frame = tb.Frame(win)
        main_frame.pack(fill="both", expand=True)

        tb.Label(main_frame, text="Select Input Folder", font=("Segoe UI", 12, "bold")).pack(pady=10)

        path_var = tk.StringVar()

        def browse_folder():
            folder = filedialog.askdirectory()
            if folder:
                path_var.set(folder)

        frame_path = tb.Frame(main_frame)
        frame_path.pack(pady=5)
        tb.Entry(frame_path, textvariable=path_var, width=42).pack(side="left", padx=5)
        tb.Button(frame_path, text="Browse", bootstyle="secondary", command=browse_folder).pack(side="left")

        step01_var = tk.BooleanVar(value=False)
        tb.Checkbutton(main_frame, text="Process Step01 Files (Skip Step01 processing)", variable=step01_var, bootstyle="round-toggle").pack(pady=14)

        def run_aae():
            folder = path_var.get().strip()
            if not folder or not os.path.isdir(folder):
                self.ui.show_error("❌ Error", "Please select a valid folder path")
                return

            def work():
                self.utils['process_aae_directory'](folder, process_step01_files=step01_var.get())
                self.ui.show_info("✅ Done", "AAE 3 Phone LSB processing complete.")

            self.run_with_loader(work)

        tb.Button(main_frame, text="Run AAE 3 Phone LSB", bootstyle="success", command=run_aae, width=22).pack(pady=12)

    # ---- Vacant Lot 6 Phone Numbers Tool (new)
    def action_vacant_lot_6_phone(self):
        win = tb.Toplevel(self.root)
        win.title("Vacant Lot — 6 Phone Numbers")
        win.geometry("560x420")
        
        main_frame = tb.Frame(win)
        main_frame.pack(fill="both", expand=True)

        tb.Label(main_frame, text="Input Folder (CSV or XLSX files)", font=("Segoe UI", 12, "bold")).pack(pady=8)
        input_var = tk.StringVar()

        def browse_input():
            folder = filedialog.askdirectory()
            if folder:
                input_var.set(folder)

        frame_in = tb.Frame(main_frame)
        frame_in.pack(pady=4)
        tb.Entry(frame_in, textvariable=input_var, width=52).pack(side="left", padx=5)
        tb.Button(frame_in, text="Browse", bootstyle="secondary", command=browse_input).pack(side="left")

        tb.Label(main_frame, text="Output folder (Processed will be created inside)", font=("Segoe UI", 10)).pack(pady=6)
        out_var = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        frame_out = tb.Frame(main_frame)
        frame_out.pack(pady=4)
        tb.Entry(frame_out, textvariable=out_var, width=42).pack(side="left", padx=5)

        def browse_out():
            d = filedialog.askdirectory()
            if d:
                out_var.set(d)

        tb.Button(frame_out, text="Browse", bootstyle="secondary", command=browse_out).pack(side="left")

        # Checkboxes for outputs — default checked
        tb.Label(main_frame, text="Which output files do you WANT to KEEP? (checked = keep)", font=("Segoe UI", 10)).pack(pady=8)

        output_labels = ["SkipTraced", "2BSkip", "CC Ready", "SC Ready", "GHL Ready", "No Hit"]
        checkbox_vars = {}
        cb_frame = tb.Frame(main_frame)
        cb_frame.pack(pady=4)
        for lbl in output_labels:
            var = tk.BooleanVar(value=True)
            checkbox_vars[lbl] = var
            tb.Checkbutton(cb_frame, text=lbl, variable=var, bootstyle="round-toggle").pack(anchor="w")

        def run_vacant():
            input_folder = input_var.get().strip()
            if not input_folder or not os.path.isdir(input_folder):
                self.ui.show_error("❌ Error", "Please select a valid input folder")
                return

            out_folder = out_var.get().strip()
            if not out_folder:
                self.ui.show_error("❌ Error", "Please select an output folder")
                return

            keep_list = [lbl for lbl, v in checkbox_vars.items() if v.get()]

            def work():
                try:
                    # loop over all CSV/XLSX files in the folder
                    for file in os.listdir(input_folder):
                        if file.endswith(".csv") or file.endswith(".xlsx"):
                            file_path = os.path.join(input_folder, file)
                            list_name = os.path.splitext(os.path.basename(file))[0]
                            self.utils['run_vacant_6_pipeline'](file_path, list_name, out_folder, keep_outputs=keep_list)
                    self.ui.show_info("✅ Done", "Vacant Lot pipeline finished for all files.")
                except Exception as e:
                    self.ui.show_error("❌ Error", f"Pipeline failed: {e}")

            self.run_with_loader(work)

        tb.Button(main_frame, text="Start List Building", bootstyle="success", command=run_vacant, width=28).pack(pady=14)


# -----------------------------
# Tool definitions (add here; UI updates automatically)
# -----------------------------
TOOL_DEFS = [
    {
        'key': 'csv2xlsx',
        'title': 'CSV → Excel',
        'desc': 'Convert one or more CSV files into clean Excel workbooks (XLSX).',
        'icon': '📄',
        'action_text': 'Convert',
    },
    {
        'key': 'xlsx2csv',
        'title': 'Excel → CSV',
        'desc': 'Export Excel workbooks into lightweight CSV format for quick use.',
        'icon': '📤',
        'action_text': 'Export',
    },
    {
        'key': 'merge',
        'title': 'File Merger',
        'desc': 'Combine multiple CSV or Excel files into a single unified workbook.',
        'icon': '🧩',
        'action_text': 'Merge',
    },
    {
        'key': 'separator',
        'title': 'Smart Separator',
        'desc': 'Split files into smaller sets based on unique column values.',
        'icon': '✂️',
        'action_text': 'Separate',
    },
    {
        'key': 'ghl',
        'title': 'GHL Compiler',
        'desc': 'Run the Step05 pipeline to generate GHL-ready deliverables.',
        'icon': '⚙️',
        'action_text': 'Compile',
    },
    {
        'key': 'mapper',
        'title': 'Column Mapper',
        'desc': 'Interactive mapping tool to align source columns to your standard.',
        'icon': '🗺️',
        'action_text': 'Map',
    },
    {
        'key': 'records',
        'title': 'Record Extractor',
        'desc': 'Extract records, zip GHL outputs, or organize structured folders.',
        'icon': '🔎',
        'action_text': 'Extract',
    },
    {
        'key': 'pipeline',
        'title': 'Bulk List Builder',
        'desc': 'Full pipeline for MCHB MPV / 6-phone vacant lot list-building.',
        'icon': '📦',
        'action_text': 'Run',
    },
    {
        'key': 'aae',
        'title': 'AAE List Builder',
        'desc': 'Process AAE lists with automated 3-phone enrichment (Step01 toggle).',
        'icon': '📱',
        'action_text': 'Run',
    },
    {
        'key': 'coladder',
        'title': 'Column Adder',
        'desc': 'Map master headers and inject new columns into your output files.',
        'icon': '➕',
        'action_text': 'Add',
    },
    {
        'key': 'recordcollector',
        'title': 'Record Collector',
        'desc': 'Collect files from multiple folders into one central repository.',
        'icon': '📂',
        'action_text': 'Collect',
    },
]

# -----------------------------
# Run app
# -----------------------------
def run_app():
    root = tb.Window(themename="cosmo")
    app = HitrotechApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()