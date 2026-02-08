import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk
import ttkbootstrap as tb

def open_merger_tool(root, ui=None):
    """
    Opens the Advanced Merge CSV/Excel Tool window.
    Features:
    - Add/Remove files dynamically
    - Key column alignment
    - Output in first selected folder
    - Plain headers (no bold, no border)
    - Merger Records.txt summary
    """
    win = tb.Toplevel(root)
    win.title("Advanced Merge CSV/Excel Files")
    win.geometry("1000x650")
    win.configure(bg="#fff3e0")

    # ----------------------------
    # Folder selection
    # ----------------------------
    tb.Label(win, text="Select Folder with CSV/XLSX Files", font=("Segoe UI", 12, "bold"),
             background="#fff3e0").pack(pady=10)
    path_var = tk.StringVar()
    first_folder_path = {"path": ""}

    frame_path = tb.Frame(win)
    frame_path.pack(pady=5)
    tb.Entry(frame_path, textvariable=path_var, width=70).pack(side="left", padx=5)

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)
            if not first_folder_path["path"]:
                first_folder_path["path"] = folder  # set first folder as output
            load_headers(folder)

    tb.Button(frame_path, text="Browse", bootstyle="secondary", command=browse_folder).pack(side="left")

    # ----------------------------
    # File TreeView
    # ----------------------------
    tree = ttk.Treeview(win, columns=("file", "headers"), show="headings", height=18)
    tree.heading("file", text="File")
    tree.heading("headers", text="Headers")
    tree.column("file", width=250, anchor="w")
    tree.column("headers", width=700, anchor="w")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    files_list = []
    file_columns = {}  # store columns of each file

    # Load headers from folder
    def load_headers(folder):
        nonlocal files_list, file_columns
        new_files = [os.path.join(folder, f)
                     for f in os.listdir(folder)
                     if f.lower().endswith(('.csv', '.xlsx', '.xls'))]

        # Add only new files
        for f in new_files:
            if f not in files_list:
                files_list.append(f)

        tree.delete(*tree.get_children())
        file_columns = {}

        for f in files_list:
            try:
                df = pd.read_csv(f, nrows=0) if f.lower().endswith(".csv") else pd.read_excel(f, nrows=0)
                cols = list(df.columns)
            except Exception as e:
                cols = [f"ERROR: {e}"]
            file_columns[f] = cols
            tree.insert("", "end", values=(os.path.basename(f), ", ".join(cols)))

    # ----------------------------
    # File remove button
    # ----------------------------
    def remove_selected_file():
        selected = tree.selection()
        for item in selected:
            fname = tree.item(item, "values")[0]
            full_path = next((f for f in files_list if os.path.basename(f) == fname), None)
            if full_path:
                files_list.remove(full_path)
                file_columns.pop(full_path, None)
            tree.delete(item)

    tb.Button(win, text="Remove Selected File", bootstyle="danger", command=remove_selected_file).pack(pady=5)

    # ----------------------------
    # Column mapping
    # ----------------------------
    tb.Label(win, text="Select Key Column to Align Across Files", font=("Segoe UI", 11, "bold"),
             background="#fff3e0").pack(pady=5)
    key_col_var = tk.StringVar()
    key_col_menu = ttk.Combobox(win, textvariable=key_col_var, width=50)
    key_col_menu.pack(pady=5)

    def refresh_key_columns():
        all_cols = set()
        for cols in file_columns.values():
            all_cols.update(cols)
        key_col_menu['values'] = list(all_cols)

    tb.Button(win, text="Refresh Columns", bootstyle="info", command=refresh_key_columns).pack(pady=5)

    # ----------------------------
    # Merge function
    # ----------------------------
    def merge_files():
        key_col = key_col_var.get().strip()
        if not files_list:
            if ui: ui.show_error("Error", "No files selected!")
            return
        if not key_col:
            if ui: ui.show_error("Error", "Select a key column first!")
            return

        dfs, record_counts = [], {}
        for f in files_list:
            df = pd.read_csv(f) if f.lower().endswith(".csv") else pd.read_excel(f)
            record_counts[os.path.basename(f)] = len(df)
            if key_col in df.columns:
                df = df.set_index(key_col)
            dfs.append(df)

        merged = pd.concat(dfs, axis=0, ignore_index=False)
        if key_col in merged.index.names:
            merged.reset_index(inplace=True)

        folder = first_folder_path["path"] if first_folder_path["path"] else os.path.dirname(files_list[0])
        output_xlsx = os.path.join(folder, "merged_output.xlsx")

        # Save Excel with plain headers (no bold, no border)
        with pd.ExcelWriter(output_xlsx, engine="xlsxwriter") as writer:
            merged.to_excel(writer, index=False, header=False, sheet_name="Sheet1", startrow=1)
            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]
            plain_fmt = workbook.add_format({"bold": False, "border": 0})
            for col_idx, name in enumerate(merged.columns):
                worksheet.write(0, col_idx, name, plain_fmt)

        # Create Merger Records.txt
        output_txt = os.path.join(folder, "Merger Records.txt")
        total_records = len(merged)
        sum_files = sum(record_counts.values())
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write("MERGER RECORDS SUMMARY\n")
            f.write("="*50 + "\n\n")
            f.write(f"Total Records After Merger: {total_records}\n\n")
            for file, count in record_counts.items():
                f.write(f"{file}: {count} records\n")
            f.write("-"*50 + "\n")
            f.write(f"--- Sum of All Files Records = {sum_files}\n")
            f.write(f"--- Total Records After Merger = {total_records}\n")

        if ui:
            ui.show_info("Success", f"Files merged!\nSaved in {folder}")

    tb.Button(win, text="Merge Files", bootstyle="success", width=20, command=merge_files).pack(pady=12)
