import os
import pandas as pd
import tkinter as tk
import ttkbootstrap as tb
from tkinter import filedialog, messagebox, ttk
import threading
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class FilesCombinationsTool:
    def __init__(self, parent):
        self.parent = parent
        self.df = None
        self.file_path = None
        self.output_path = None
        self.combination_entries = []
        self.progress = None
        
    def open_tool_window(self):
        self.win = tb.Toplevel(self.parent)
        self.win.title("📊 Files Combinations Tool")
        self.win.geometry("900x700")
        self.win.minsize(800, 600)
        
        # Main frame with notebook for tabs
        main_frame = tb.Frame(self.win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # File Selection Tab
        file_tab = tb.Frame(self.notebook, padding=10)
        self.notebook.add(file_tab, text="📁 File Selection")
        
        self.setup_file_tab(file_tab)
        
        # Combinations Tab
        comb_tab = tb.Frame(self.notebook, padding=10)
        self.notebook.add(comb_tab, text="⚙️ Combinations")
        
        self.setup_combinations_tab(comb_tab)
        
        # Initially disable combinations tab
        self.notebook.tab(1, state="disabled")
        
        # Status bar
        status_frame = tb.Frame(main_frame)
        status_frame.pack(fill="x", pady=(5, 0))
        
        self.status_label = tb.Label(status_frame, text="Ready to load file", bootstyle="info", font=("Segoe UI", 9))
        self.status_label.pack(side="left")
        
        # Fixed progress bar - removed height parameter
        self.progress = tb.Progressbar(status_frame, mode='indeterminate', bootstyle="success-striped")
        self.progress.pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def setup_file_tab(self, parent):
        # File selection section
        file_frame = tb.LabelFrame(parent, text="📄 Source File", bootstyle="primary", padding=10)
        file_frame.pack(fill="x", pady=(0, 15))
        
        tb.Label(file_frame, text="Select CSV or Excel file:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        
        file_select_frame = tb.Frame(file_frame)
        file_select_frame.pack(fill="x", pady=4)
        
        self.file_path_var = tk.StringVar()
        file_entry = tb.Entry(file_select_frame, textvariable=self.file_path_var, font=("Segoe UI", 9))
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        btn_frame = tb.Frame(file_select_frame)
        btn_frame.pack(side="right")
        
        tb.Button(btn_frame, text="Browse", bootstyle="primary-outline", 
                 command=self.browse_file, width=8).pack(side="left", padx=(0, 4))
        tb.Button(btn_frame, text="Load", bootstyle="success", 
                 command=self.load_file, width=6).pack(side="left")
        
        # Output directory section
        output_frame = tb.LabelFrame(parent, text="📂 Output Location", bootstyle="info", padding=10)
        output_frame.pack(fill="x", pady=(0, 15))
        
        tb.Label(output_frame, text="Output folder:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        
        output_select_frame = tb.Frame(output_frame)
        output_select_frame.pack(fill="x", pady=4)
        
        self.output_path_var = tk.StringVar()
        output_entry = tb.Entry(output_select_frame, textvariable=self.output_path_var, font=("Segoe UI", 9))
        output_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        tb.Button(output_select_frame, text="Browse", bootstyle="info-outline", 
                 command=self.browse_output, width=8).pack(side="right")
        
        # File info section
        info_frame = tb.LabelFrame(parent, text="📊 File Information", bootstyle="secondary", padding=10)
        info_frame.pack(fill="both", expand=True)
        
        # Create info labels
        info_grid = tb.Frame(info_frame)
        info_grid.pack(fill="both", expand=True)
        
        self.info_labels = {
            'records': tb.Label(info_grid, text="Total Records: -", font=("Segoe UI", 9)),
            'columns': tb.Label(info_grid, text="Total Columns: -", font=("Segoe UI", 9)),
            'size': tb.Label(info_grid, text="File Size: -", font=("Segoe UI", 9)),
            'modified': tb.Label(info_grid, text="Last Modified: -", font=("Segoe UI", 9))
        }
        
        for i, (key, label) in enumerate(self.info_labels.items()):
            label.grid(row=i//2, column=i%2, sticky="w", padx=8, pady=3)
    
    def setup_combinations_tab(self, parent):
        # Columns display section
        columns_frame = tb.LabelFrame(parent, text="📋 File Columns", bootstyle="primary", padding=10)
        columns_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Column selection
        col_select_frame = tb.Frame(columns_frame)
        col_select_frame.pack(fill="x", pady=(0, 8))
        
        tb.Label(col_select_frame, text="Select column for combinations:", 
                font=("Segoe UI", 10, "bold")).pack(side="left")
        
        self.column_var = tk.StringVar()
        self.column_combo = ttk.Combobox(col_select_frame, textvariable=self.column_var, 
                                       state="readonly", width=25, font=("Segoe UI", 9))
        self.column_combo.pack(side="left", padx=(8, 0))
        
        # Treeview for columns
        tree_frame = tb.Frame(columns_frame)
        tree_frame.pack(fill="both", expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=("Type", "Unique", "Nulls"), 
                               show="headings", height=6)
        self.tree.heading("#0", text="Column Name", anchor="w")
        self.tree.heading("Type", text="Data Type", anchor="w")
        self.tree.heading("Unique", text="Unique Values", anchor="w")
        self.tree.heading("Nulls", text="Null Values", anchor="w")
        
        self.tree.column("#0", width=180, anchor="w")
        self.tree.column("Type", width=90, anchor="w")
        self.tree.column("Unique", width=90, anchor="w")
        self.tree.column("Nulls", width=80, anchor="w")
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Combinations section
        comb_frame = tb.LabelFrame(parent, text="🎯 Combination Requirements", bootstyle="info", padding=10)
        comb_frame.pack(fill="x", pady=(0, 15))
        
        # Summary frame
        summary_frame = tb.Frame(comb_frame)
        summary_frame.pack(fill="x", pady=(0, 8))
        
        self.summary_label = tb.Label(summary_frame, text="Total requested: 0 records", 
                                    font=("Segoe UI", 9, "bold"))
        self.summary_label.pack(anchor="w")
        
        # Combination entries frame with scrollbar
        comb_entries_container = tb.Frame(comb_frame)
        comb_entries_container.pack(fill="both", expand=True, pady=(0, 8))
        
        # Canvas and scrollbar for combination entries
        canvas = tk.Canvas(comb_entries_container, height=120)
        scrollbar = ttk.Scrollbar(comb_entries_container, orient="vertical", command=canvas.yview)
        self.comb_entries_frame = tb.Frame(canvas)
        
        self.comb_entries_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.comb_entries_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add/Remove buttons
        btn_frame = tb.Frame(comb_frame)
        btn_frame.pack(fill="x")
        
        tb.Button(btn_frame, text="➕ Add", bootstyle="success-outline",
                 command=self.add_combination_entry, width=8).pack(side="left", padx=(0, 6))
        tb.Button(btn_frame, text="➖ Remove", bootstyle="danger-outline",
                 command=self.remove_combination_entry, width=8).pack(side="left", padx=(0, 6))
        tb.Button(btn_frame, text="🗑️ Clear All", bootstyle="warning-outline",
                 command=self.clear_combinations, width=10).pack(side="left")
        
        # Add initial combination entry
        self.add_combination_entry()
        
        # Action buttons - Moved to bottom right corner
        action_frame = tb.Frame(parent)
        action_frame.pack(fill="x", pady=(10, 0))
        
        # Right-aligned action buttons
        right_frame = tb.Frame(action_frame)
        right_frame.pack(side="right")
        
        tb.Button(right_frame, text="▶️ Run", bootstyle="success",
                 command=self.start_combination, width=8).pack(side="left", padx=(0, 6))
        tb.Button(right_frame, text="❌ Close", bootstyle="danger",
                 command=self.win.destroy, width=8).pack(side="left")
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV or Excel file",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            self.file_path_var.set(file_path)
            
            # Set default output path to same directory as input file
            output_dir = os.path.dirname(file_path)
            self.output_path_var.set(output_dir)
            self.output_path = output_dir
    
    def browse_output(self):
        output_path = filedialog.askdirectory(
            title="Select Output Folder"
        )
        
        if output_path:
            self.output_path_var.set(output_path)
            self.output_path = output_path
    
    def load_file(self):
        if not self.file_path_var.get():
            messagebox.showerror("Error", "Please select a file first")
            return
        
        try:
            if self.progress:
                self.progress.start()
            self.status_label.config(text="Loading file...")
            
            file_path = self.file_path_var.get()
            
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path, encoding='utf-8')
            else:
                self.df = pd.read_excel(file_path)
            
            # Update file info
            self.update_file_info(file_path)
            
            # Populate columns tree
            self.populate_columns_tree()
            
            # Enable combinations tab
            self.notebook.tab(1, state="normal")
            self.notebook.select(1)  # Switch to combinations tab
            
            self.status_label.config(text=f"Loaded {len(self.df):,} records successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            self.status_label.config(text="Error loading file")
        finally:
            if self.progress:
                self.progress.stop()
    
    def update_file_info(self, file_path):
        # Get file stats
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        modified_time = datetime.fromtimestamp(file_stats.st_mtime)
        
        # Update info labels
        self.info_labels['records'].config(text=f"Total Records: {len(self.df):,}")
        self.info_labels['columns'].config(text=f"Total Columns: {len(self.df.columns):,}")
        self.info_labels['size'].config(text=f"File Size: {file_size/1024/1024:.2f} MB")
        self.info_labels['modified'].config(text=f"Last Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def populate_columns_tree(self):
        # Clear existing tree items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate tree with column info
        columns = []
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            unique_count = self.df[col].nunique()
            null_count = self.df[col].isnull().sum()
            
            self.tree.insert("", "end", text=col, values=(dtype, f"{unique_count:,}", f"{null_count:,}"))
            columns.append(col)
        
        # Update column combo
        self.column_combo['values'] = columns
        if columns:
            self.column_var.set(columns[0])
    
    def add_combination_entry(self):
        entry_num = len(self.combination_entries) + 1
        frame = tb.Frame(self.comb_entries_frame)
        frame.pack(fill="x", pady=1, padx=2)
        
        tb.Label(frame, text=f"C{entry_num}:", width=4, anchor="w", font=("Segoe UI", 9)).pack(side="left")
        
        entry = tb.Entry(frame, width=8, justify="right", font=("Segoe UI", 9))
        entry.pack(side="left", padx=(2, 2))
        entry.insert(0, "1000")
        
        tb.Label(frame, text="records", font=("Segoe UI", 9)).pack(side="left", padx=(2, 0))
        
        # Add validation
        entry.config(validate="key", validatecommand=(frame.register(self.validate_number), '%P'))
        
        self.combination_entries.append(entry)
        entry.bind('<KeyRelease>', self.update_summary)
        
        self.update_summary()
    
    def remove_combination_entry(self):
        if self.combination_entries:
            last_entry = self.combination_entries.pop()
            last_entry.master.destroy()
            self.update_summary()
    
    def clear_combinations(self):
        for entry in self.combination_entries[:]:
            self.remove_combination_entry()
        self.add_combination_entry()  # Add one empty entry back
    
    def validate_number(self, value):
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def update_summary(self, event=None):
        total = 0
        for entry in self.combination_entries:
            try:
                total += int(entry.get() or 0)
            except ValueError:
                pass
        
        available = len(self.df) if self.df is not None else 0
        self.summary_label.config(text=f"Total requested: {total:,} records (Available: {available:,})")
        
        # Color coding based on available records
        if total > available:
            self.summary_label.config(bootstyle="danger")
        elif total == available:
            self.summary_label.config(bootstyle="warning")
        else:
            self.summary_label.config(bootstyle="success")
    
    def start_combination(self):
        if self.df is None:
            messagebox.showerror("Error", "Please load a file first")
            return
        
        if not self.column_var.get():
            messagebox.showerror("Error", "Please select a column for combinations")
            return
        
        if not self.output_path:
            messagebox.showerror("Error", "Please select an output folder")
            return
        
        # Get combination requirements
        comb_requirements = []
        total_requested = 0
        
        for i, entry in enumerate(self.combination_entries):
            try:
                count = int(entry.get() or 0)
                if count <= 0:
                    continue
                comb_requirements.append((f"Combination_{i+1}", count))
                total_requested += count
            except ValueError:
                messagebox.showerror("Error", f"Invalid number in combination {i+1}")
                return
        
        if total_requested == 0:
            messagebox.showerror("Error", "Please specify at least one combination requirement")
            return
        
        if total_requested > len(self.df):
            if not messagebox.askyesno("Warning", 
                f"Total requested records ({total_requested:,}) exceed available records ({len(self.df):,}). "
                "Do you want to continue with maximum available records?"):
                return
        
        # Start processing
        if self.progress:
            self.progress.start()
        self.status_label.config(text="Processing combinations...")
        
        thread = threading.Thread(
            target=self.process_combinations,
            args=(comb_requirements,)
        )
        thread.daemon = True
        thread.start()
    
    def process_combinations(self, comb_requirements):
        try:
            selected_column = self.column_var.get()
            base_name = Path(self.file_path).stem
            output_dir = Path(self.output_path)
            processed_dir = output_dir / f"{base_name}_combinations"
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            # Group records by the selected column value
            grouped_records = defaultdict(list)
            for idx, row in self.df.iterrows():
                group_key = row[selected_column]
                grouped_records[group_key].append(idx)
            
            # Convert to list of (group_key, record_count, record_indices)
            groups = []
            for key, indices in grouped_records.items():
                groups.append((key, len(indices), indices))
            
            # Sort groups by size (largest first for better fitting)
            groups.sort(key=lambda x: x[1], reverse=True)
            
            remaining_groups = groups.copy()
            results = {}
            
            for name, requested_count in comb_requirements:
                if not remaining_groups:
                    break
                
                selected_indices = []
                current_count = 0
                selected_groups = []
                
                # Try to find the best combination of groups that fits the requested count
                for i, (key, count, indices) in enumerate(remaining_groups):
                    if current_count + count <= requested_count:
                        selected_indices.extend(indices)
                        current_count += count
                        selected_groups.append((key, count))
                    elif current_count == 0 and count > requested_count:
                        # If a single group is larger than requested, take it anyway
                        selected_indices.extend(indices)
                        current_count = count
                        selected_groups.append((key, count))
                        break
                
                # Remove selected groups from remaining
                if selected_groups:
                    # Create a mask for groups to keep
                    groups_to_keep = []
                    for group in remaining_groups:
                        keep = True
                        for selected_key, selected_count in selected_groups:
                            if group[0] == selected_key and group[1] == selected_count:
                                keep = False
                                break
                        if keep:
                            groups_to_keep.append(group)
                    remaining_groups = groups_to_keep
                
                if not selected_indices:
                    continue
                
                # Create the combination
                combined_sample = self.df.loc[selected_indices]
                actual_count = len(combined_sample)
                
                # Save the combination
                comb_dir = processed_dir / f"{name}_{actual_count}_records"
                comb_dir.mkdir(exist_ok=True)
                
                output_file = comb_dir / f"{base_name}_{name}.csv"
                combined_sample.to_csv(output_file, index=False)
                
                # Create detailed info file
                info_file = comb_dir / "combination_info.txt"
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"Combination Analysis Report\n")
                    f.write(f"{'='*50}\n\n")
                    f.write(f"Source File: {self.file_path}\n")
                    f.write(f"Combination Name: {name}\n")
                    f.write(f"Requested Records: {requested_count:,}\n")
                    f.write(f"Actual Records: {actual_count:,}\n")
                    f.write(f"Source Column: {selected_column}\n")
                    f.write(f"Unique Groups: {len(selected_groups):,}\n")
                    f.write(f"Total Groups: {len(groups):,}\n")
                    f.write(f"Groups Used:\n")
                    for key, count in selected_groups:
                        f.write(f"  - {key}: {count} records\n")
                    f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                results[name] = actual_count
            
            # Save remaining records if any
            if remaining_groups:
                remaining_indices = []
                for key, count, indices in remaining_groups:
                    remaining_indices.extend(indices)
                
                if remaining_indices:
                    remaining_df = self.df.loc[remaining_indices]
                    remaining_dir = processed_dir / "Remaining_Records"
                    remaining_dir.mkdir(exist_ok=True)
                    
                    remaining_file = remaining_dir / f"{base_name}_remaining.csv"
                    remaining_df.to_csv(remaining_file, index=False)
                    
                    info_file = remaining_dir / "remaining_info.txt"
                    with open(info_file, 'w', encoding='utf-8') as f:
                        f.write(f"Remaining Records Analysis\n")
                        f.write(f"{'='*40}\n\n")
                        f.write(f"Total Remaining: {len(remaining_df):,} records\n")
                        f.write(f"Remaining Groups: {len(remaining_groups):,}\n")
                        f.write(f"Source Column: {selected_column}\n")
                        f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Update UI in main thread
            self.parent.after(0, self.combination_complete, results, str(processed_dir))
            
        except Exception as e:
            self.parent.after(0, self.combination_error, str(e))
    
    def combination_complete(self, results, output_dir):
        if self.progress:
            self.progress.stop()
        
        result_text = "✅ Combination completed successfully!\n\n"
        result_text += f"📁 Output directory: {output_dir}\n\n"
        result_text += "📊 Results:\n"
        
        total_processed = 0
        for name, count in results.items():
            result_text += f"   • {name}: {count:,} records\n"
            total_processed += count
        
        result_text += f"\n📈 Total processed: {total_processed:,} records\n"
        
        if self.df is not None:
            remaining = len(self.df) - total_processed
            result_text += f"📉 Remaining: {remaining:,} records\n"
            result_text += f"🎯 Efficiency: {(total_processed/len(self.df)*100):.1f}%"
        
        self.status_label.config(text="Processing completed")
        messagebox.showinfo("Success", result_text)
    
    def combination_error(self, error_msg):
        if self.progress:
            self.progress.stop()
        self.status_label.config(text="Error during processing")
        messagebox.showerror("Error", f"Processing failed:\n{error_msg}")