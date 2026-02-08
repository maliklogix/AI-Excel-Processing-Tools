import os
import tkinter as tk
import ttkbootstrap as tb
from tkinter import filedialog, ttk

from main.main import HitrotechApp, TOOL_DEFS  # Import base app + tools
# from logs import report_summary_logs
# from logs.report_summary_logs import logger, log_tool_usage, open_today_report_folder

import subprocess
import pandas as pd
import threading

# Import the new subtractor script
from utils.records_subtractor import subtract_records, subtract_folders

# -----------------------------
# Extended Application
# -----------------------------
class ExtendedApp(HitrotechApp):
    def __init__(self, root):
        super().__init__(root)

    # ---- File Records Subtractor Tool
    def action_file_subtractor(self):
        win = tb.Toplevel(self.root)
        win.title("File Records Subtractor")
        win.geometry("900x800")
        
        # Use a regular tkinter Frame for the background
        main_frame = tk.Frame(win, bg="#fff3e0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame, bg="#fff3e0")
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#fff3e0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Left side files selection
        left_frame = tb.LabelFrame(scrollable_frame, text="Left Side Files (Records to keep)", bootstyle="primary")
        left_frame.pack(fill="x", padx=10, pady=5)
        
        tb.Label(left_frame, text="Select files containing records to keep (subtract from)").pack(pady=5)
        
        left_files_frame = tk.Frame(left_frame)
        left_files_frame.pack(fill="x", padx=5, pady=5)
        
        left_files_listbox = tk.Listbox(left_files_frame, height=6, selectmode=tk.EXTENDED)
        left_scrollbar = ttk.Scrollbar(left_files_frame, orient="vertical", command=left_files_listbox.yview)
        left_files_listbox.configure(yscrollcommand=left_scrollbar.set)
        
        left_files_listbox.pack(side="left", fill="both", expand=True)
        left_scrollbar.pack(side="right", fill="y")
        
        left_btn_frame = tb.Frame(left_frame)
        left_btn_frame.pack(fill="x", padx=5, pady=5)
        
        def add_left_files():
            files = filedialog.askopenfilenames(
                title="Select Left Side Files",
                filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx"), ("All Files", "*.*")]
            )
            for file in files:
                left_files_listbox.insert(tk.END, file)
            update_column_lists()
        
        def remove_left_files():
            selected_indices = left_files_listbox.curselection()
            for index in selected_indices[::-1]:
                left_files_listbox.delete(index)
            update_column_lists()
        
        tb.Button(left_btn_frame, text="Add Files", bootstyle="secondary", 
                 command=add_left_files).pack(side="left", padx=5)
        tb.Button(left_btn_frame, text="Remove Selected", bootstyle="danger", 
                 command=remove_left_files).pack(side="left", padx=5)
        tb.Button(left_btn_frame, text="Clear All", bootstyle="warning", 
                 command=lambda: left_files_listbox.delete(0, tk.END)).pack(side="left", padx=5)
        
        tb.Label(left_frame, text="Combine columns (comma-separated):").pack(pady=5)
        left_columns_var = tk.StringVar()
        left_columns_entry = tb.Combobox(left_frame, textvariable=left_columns_var, width=50)
        left_columns_entry.pack(pady=5)
        
        # Right side files selection
        right_frame = tb.LabelFrame(scrollable_frame, text="Right Side Files (Records to subtract)", bootstyle="danger")
        right_frame.pack(fill="x", padx=10, pady=5)
        
        tb.Label(right_frame, text="Select files containing records to subtract").pack(pady=5)
        
        right_files_frame = tk.Frame(right_frame)
        right_files_frame.pack(fill="x", padx=5, pady=5)
        
        right_files_listbox = tk.Listbox(right_files_frame, height=6, selectmode=tk.EXTENDED)
        right_scrollbar = ttk.Scrollbar(right_files_frame, orient="vertical", command=right_files_listbox.yview)
        right_files_listbox.configure(yscrollcommand=right_scrollbar.set)
        
        right_files_listbox.pack(side="left", fill="both", expand=True)
        right_scrollbar.pack(side="right", fill="y")
        
        right_btn_frame = tb.Frame(right_frame)
        right_btn_frame.pack(fill="x", padx=5, pady=5)
        
        def add_right_files():
            files = filedialog.askopenfilenames(
                title="Select Right Side Files",
                filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx"), ("All Files", "*.*")]
            )
            for file in files:
                right_files_listbox.insert(tk.END, file)
            update_column_lists()
        
        def remove_right_files():
            selected_indices = right_files_listbox.curselection()
            for index in selected_indices[::-1]:
                right_files_listbox.delete(index)
            update_column_lists()
        
        tb.Button(right_btn_frame, text="Add Files", bootstyle="secondary", 
                 command=add_right_files).pack(side="left", padx=5)
        tb.Button(right_btn_frame, text="Remove Selected", bootstyle="danger", 
                 command=remove_right_files).pack(side="left", padx=5)
        tb.Button(right_btn_frame, text="Clear All", bootstyle="warning", 
                 command=lambda: right_files_listbox.delete(0, tk.END)).pack(side="left", padx=5)
        
        tb.Label(right_frame, text="Combine columns (comma-separated):").pack(pady=5)
        right_columns_var = tk.StringVar()
        right_columns_entry = tb.Combobox(right_frame, textvariable=right_columns_var, width=50)
        right_columns_entry.pack(pady=5)
        
        # Mapping visualization frame
        mapping_frame = tb.LabelFrame(scrollable_frame, text="Column Mapping Visualization", bootstyle="info")
        mapping_frame.pack(fill="x", padx=10, pady=10)
        
        mapping_canvas = tk.Canvas(mapping_frame, height=100, bg="white", highlightthickness=1, highlightbackground="#ccc")
        mapping_canvas.pack(fill="x", padx=5, pady=5)
        
        left_mapping_text = mapping_canvas.create_text(150, 30, text="Left Columns: Not set", font=("Arial", 10), fill="blue")
        right_mapping_text = mapping_canvas.create_text(150, 70, text="Right Columns: Not set", font=("Arial", 10), fill="red")
        mapping_status = mapping_canvas.create_text(450, 50, text="Mapping Status: Not configured", font=("Arial", 10, "bold"), fill="orange")
        
        def update_mapping_display():
            left_cols = left_columns_var.get()
            right_cols = right_columns_var.get()
            
            mapping_canvas.itemconfig(left_mapping_text, text=f"Left Columns: {left_cols if left_cols else 'Not set'}")
            mapping_canvas.itemconfig(right_mapping_text, text=f"Right Columns: {right_cols if right_cols else 'Not set'}")
            
            if left_cols and right_cols:
                mapping_canvas.itemconfig(mapping_status, text="Mapping Status: ✅ Ready to subtract", fill="green")
            elif left_cols or right_cols:
                mapping_canvas.itemconfig(mapping_status, text="Mapping Status: ⚠️ Partial configuration", fill="orange")
            else:
                mapping_canvas.itemconfig(mapping_status, text="Mapping Status: ❌ Not configured", fill="red")
        
        # Bind the update function to column entry changes
        left_columns_var.trace("w", lambda *args: update_mapping_display())
        right_columns_var.trace("w", lambda *args: update_mapping_display())
        
        # Function to update column lists from files
        def update_column_lists():
            try:
                # Get columns from first left file if available
                left_files = left_files_listbox.get(0, tk.END)
                if left_files:
                    file = left_files[0]
                    if file.endswith('.csv'):
                        df = pd.read_csv(file, nrows=1)
                    else:
                        df = pd.read_excel(file, nrows=1)
                    left_cols = list(df.columns)
                    left_columns_entry['values'] = left_cols
                
                # Get columns from first right file if available
                right_files = right_files_listbox.get(0, tk.END)
                if right_files:
                    file = right_files[0]
                    if file.endswith('.csv'):
                        df = pd.read_csv(file, nrows=1)
                    else:
                        df = pd.read_excel(file, nrows=1)
                    right_cols = list(df.columns)
                    right_columns_entry['values'] = right_cols
                    
            except Exception as e:
                print(f"Error reading column names: {e}")
        
        # Output options
        output_frame = tb.LabelFrame(scrollable_frame, text="Output Options", bootstyle="success")
        output_frame.pack(fill="x", padx=10, pady=5)
        
        output_name_frame = tb.Frame(output_frame)
        output_name_frame.pack(fill="x", padx=5, pady=5)
        
        tb.Label(output_name_frame, text="Output file name:").pack(side="left")
        output_name_var = tk.StringVar(value="Records_Minus")
        tb.Entry(output_name_frame, textvariable=output_name_var, width=30).pack(side="left", padx=10)
        
        output_format_var = tk.StringVar(value="xlsx")
        format_frame = tb.Frame(output_name_frame)
        format_frame.pack(side="left", padx=20)
        tb.Label(format_frame, text="Format:").pack(side="left")
        tb.Radiobutton(format_frame, text="Excel", variable=output_format_var, value="xlsx", bootstyle="success").pack(side="left", padx=5)
        tb.Radiobutton(format_frame, text="CSV", variable=output_format_var, value="csv", bootstyle="success").pack(side="left", padx=5)
        
        output_folder_frame = tb.Frame(output_frame)
        output_folder_frame.pack(fill="x", padx=5, pady=5)
        
        tb.Label(output_folder_frame, text="Output folder:").pack(side="left")
        output_folder_var = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        tb.Entry(output_folder_frame, textvariable=output_folder_var, width=40).pack(side="left", padx=10)
        
        def browse_output_folder():
            folder = filedialog.askdirectory()
            if folder:
                output_folder_var.set(folder)
        
        tb.Button(output_folder_frame, text="Browse", bootstyle="secondary", 
                 command=browse_output_folder).pack(side="left", padx=5)
        
        # Progress bar
        progress_frame = tb.Frame(scrollable_frame)
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = tb.Progressbar(progress_frame, variable=progress_var, maximum=100, bootstyle="success-striped")
        progress_bar.pack(fill="x", pady=5)
        
        progress_label = tb.Label(progress_frame, text="Ready", font=("Arial", 9))
        progress_label.pack()
        
        # Run button
        def run_subtraction():
            left_files = left_files_listbox.get(0, tk.END)
            right_files = right_files_listbox.get(0, tk.END)
            
            if not left_files:
                self.ui.show_error("❌ Error", "Please select at least one left side file")
                return
            
            if not right_files:
                self.ui.show_error("❌ Error", "Please select at least one right side file")
                return
            
            left_columns = [col.strip() for col in left_columns_var.get().split(",") if col.strip()]
            right_columns = [col.strip() for col in right_columns_var.get().split(",") if col.strip()]
            
            if not left_columns:
                self.ui.show_error("❌ Error", "Please specify columns to combine for left side files")
                return
            
            if not right_columns:
                self.ui.show_error("❌ Error", "Please specify columns to combine for right side files")
                return
            
            output_folder = output_folder_var.get()
            if not output_folder:
                self.ui.show_error("❌ Error", "Please select an output folder")
                return
            
            os.makedirs(output_folder, exist_ok=True)
            
            output_name = output_name_var.get()
            if not output_name:
                output_name = "Records_Minus"
            
            output_format = output_format_var.get()
            output_path = os.path.join(output_folder, f"{output_name}.{output_format}")
            
            def work():
                try:
                    progress_var.set(10)
                    progress_label.config(text="Starting subtraction...")
                    
                    # Use the standalone subtractor function
                    subtract_records(
                        left_files=list(left_files),
                        right_files=list(right_files),
                        left_columns=left_columns,
                        right_columns=right_columns,
                        output_path=output_path,
                        output_format=output_format
                    )
                    
                    progress_var.set(100)
                    progress_label.config(text="✅ Subtraction completed!")
                    
                    self.ui.show_info("✅ Success", f"Subtraction completed. Result saved to:\n{output_path}")
                    
                except Exception as e:
                    progress_label.config(text="❌ Error occurred!")
                    self.ui.show_error("❌ Error", f"An error occurred during subtraction:\n{str(e)}")
            
            # Run in a separate thread
            thread = threading.Thread(target=work)
            thread.daemon = True
            thread.start()
        
        action_frame = tb.Frame(scrollable_frame)
        action_frame.pack(pady=10)
        
        tb.Button(action_frame, text="🔄 Update Column Lists", bootstyle="info", 
                 command=update_column_lists).pack(side="left", padx=5)
        tb.Button(action_frame, text="➖ Subtract Files", bootstyle="success", 
                 command=run_subtraction, width=20).pack(side="left", padx=5)
        
        # Initialize
        update_mapping_display()

    # ---- Vacant Lot 6 Phone Numbers Tool
    def action_vacant_lot_6_phone(self):
        win = tb.Toplevel(self.root)
        win.title("Vacant Lot —  Phone Numbers")
        win.geometry("560x420")
        
        # Use regular tkinter Frame for background
        main_frame = tk.Frame(win, bg="#fff3e0")
        main_frame.pack(fill="both", expand=True)

        tb.Label(main_frame, text="Input Folder (CSV or XLSX files)", font=("Segoe UI", 12, "bold"), background="#fff3e0").pack(pady=8)
        input_var = tk.StringVar()

        def browse_input():
            folder = filedialog.askdirectory()
            if folder:
                input_var.set(folder)

        frame_in = tb.Frame(main_frame)
        frame_in.pack(pady=4)
        tb.Entry(frame_in, textvariable=input_var, width=52).pack(side="left", padx=5)
        tb.Button(frame_in, text="Browse", bootstyle="secondary", command=browse_input).pack(side="left")

        tb.Label(main_frame, text="Output folder (Processed will be created inside)", font=("Segoe UI", 10), background="#fff3e0").pack(pady=6)
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
        tb.Label(main_frame, text="Which output files do you WANT to KEEP? (checked = keep)", font=("Segoe UI", 10), background="#fff3e0").pack(pady=8)

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
                    for file in os.listdir(input_folder):
                        if file.endswith(".csv") or file.endswith(".xlsx"):
                            file_path = os.path.join(input_folder, file)
                            list_name = os.path.splitext(os.path.basename(file))[0]
                            self.utils['run_vacant_6_pipeline'](
                                file_path, list_name, out_folder, keep_outputs=keep_list
                            )
                    self.ui.show_info("✅ Done", "Vacant Lot pipeline finished for all files.")
                except Exception as e:
                    self.ui.show_error("❌ Error", f"Pipeline failed: {e}")

            self.run_with_loader(work)

        tb.Button(main_frame, text="Start List Building", bootstyle="success", command=run_vacant, width=28).pack(pady=14)

    # ---- Extend handlers
    def get_action_handlers(self):
        handlers = super().get_action_handlers()
        handlers['vacant6'] = self.action_vacant_lot_6_phone
        handlers['filesubtractor'] = self.action_file_subtractor
        return handlers


# -----------------------------
# Add tool definition for Vacant Lot and File Subtractor
# -----------------------------
TOOL_DEFS.append({
    'key': 'vacant6',
    'title': 'List Builder-Land Data',
    'desc': '6 Phone Vacant Lot',
    'icon': '🌿',
    'action_text': 'Run',
})

TOOL_DEFS.append({
    'key': 'filesubtractor',
    'title': 'File Records Subtractor',
    'desc': 'Subtract records from one set of files from another',
    'icon': '➖',
    'action_text': 'Open',
})