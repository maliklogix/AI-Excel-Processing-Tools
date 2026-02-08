# utils/gen_coloumns_adder.py
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk
import ttkbootstrap as tb

# ---------------------------------------
# Core Logic
# ---------------------------------------
def apply_column_addition(master_file, folder, mappings):
    status_text = ""

    try:
        master_df = pd.read_excel(master_file, dtype=str)

        # pick first file columns for reference
        sample_file = None
        for f in os.listdir(folder):
            if f.endswith(".xlsx"):
                sample_file = os.path.join(folder, f)
                break
        if not sample_file:
            return "❌ No Excel file found in folder."

        for f in os.listdir(folder):
            if not f.endswith(".xlsx"):
                continue
            file_path = os.path.join(folder, f)
            df = pd.read_excel(file_path, dtype=str)

            for src_col, new_col, after_col in mappings:
                if src_col not in master_df.columns:
                    continue

                # create a map from master
                map_dict = dict(zip(master_df[src_col], master_df[new_col]))
                df[new_col] = df[src_col].map(map_dict)

                # reorder if requested
                if after_col and after_col in df.columns:
                    cols = list(df.columns)
                    cols.remove(new_col)
                    insert_at = cols.index(after_col) + 1
                    cols.insert(insert_at, new_col)
                    df = df[cols]

            df.to_excel(file_path, index=False)

        status_text = f"✅ Columns added successfully into {folder}"
    except Exception as e:
        status_text = f"❌ Failed: {e}"

    return status_text


# ---------------------------------------
# Dashboard
# ---------------------------------------
def run_column_adder(root):
    win = tb.Toplevel(root)
    win.title("Column Adder Dashboard")
    win.geometry("1000x700")
    win.configure(padx=15, pady=15)

    master_var = tk.StringVar()
    folder_var = tk.StringVar()
    status_var = tk.StringVar(value="Ready")

    master_cols = []
    target_cols = []

    # --- Top section
    top_frame = tb.Frame(win)
    top_frame.pack(fill="x", pady=8)

    tb.Label(top_frame, text="Master File:", font=("Segoe UI", 11, "bold")).pack(side="left")
    tb.Entry(top_frame, textvariable=master_var, width=50).pack(side="left", padx=6)
    tb.Button(top_frame, text="Browse", command=lambda: select_master()).pack(side="left")

    tb.Label(top_frame, text="   Folder:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(20,0))
    tb.Entry(top_frame, textvariable=folder_var, width=40).pack(side="left", padx=6)
    tb.Button(top_frame, text="Browse", command=lambda: select_folder()).pack(side="left")

    # --- Mapping Section (drag-drop style simplified as dual listboxes)
    mapping_frame = tb.LabelFrame(win, text="Column Mapping", padding=10)
    mapping_frame.pack(fill="both", expand=True, pady=10)

    left_list = tk.Listbox(mapping_frame, selectmode="single", height=12, exportselection=False)
    right_list = tk.Listbox(mapping_frame, selectmode="single", height=12, exportselection=False)
    map_list = tk.Listbox(mapping_frame, selectmode="single", height=12)

    left_list.pack(side="left", fill="y", padx=8)
    tb.Label(mapping_frame, text="==>").pack(side="left")
    right_list.pack(side="left", fill="y", padx=8)
    map_list.pack(side="left", fill="y", padx=8)

    def add_map():
        if left_list.curselection() and right_list.curselection():
            l = left_list.get(left_list.curselection())
            r = right_list.get(right_list.curselection())
            map_list.insert("end", f"{l} == {r}")

    def clear_map():
        map_list.delete("active")

    btns = tb.Frame(mapping_frame)
    btns.pack(side="left", padx=8)
    tb.Button(btns, text="Map", command=add_map).pack(fill="x", pady=2)
    tb.Button(btns, text="Remove", command=clear_map, bootstyle="danger").pack(fill="x", pady=2)

    # --- New Columns Section
    newcols_frame = tb.LabelFrame(win, text="New Columns", padding=10)
    newcols_frame.pack(fill="x", pady=10)

    newcol_rows = []

    def add_newcol_row():
        row = tb.Frame(newcols_frame)
        row.pack(fill="x", pady=3)

        src_dd = ttk.Combobox(row, values=master_cols, width=20)
        src_dd.pack(side="left", padx=5)

        newname_entry = ttk.Entry(row, width=20)
        newname_entry.pack(side="left", padx=5)

        after_dd = ttk.Combobox(row, values=target_cols, width=20)
        after_dd.pack(side="left", padx=5)

        rm_btn = tb.Button(row, text="❌", bootstyle="danger", command=lambda: (row.destroy(), newcol_rows.remove((src_dd, newname_entry, after_dd))))
        rm_btn.pack(side="left", padx=5)

        newcol_rows.append((src_dd, newname_entry, after_dd))

    tb.Button(newcols_frame, text="➕ Add Column", bootstyle="primary", command=add_newcol_row).pack(anchor="w", pady=4)

    # --- Run Button
    def run():
        mappings = []
        for src, newname, after in newcol_rows:
            if src.get() and newname.get():
                mappings.append((src.get(), newname.get(), after.get()))
        if not mappings:
            status_var.set("⚠️ No new column mappings added.")
            return
        status_var.set("⏳ Running...")
        status = apply_column_addition(master_var.get(), folder_var.get(), mappings)
        status_var.set(status)

    tb.Button(win, text="Run Column Addition", bootstyle="success", command=run).pack(pady=10)

    # --- Status Bar
    tb.Label(win, textvariable=status_var, font=("Segoe UI", 10), bootstyle="inverse-dark").pack(fill="x", pady=5)

    # --- Selectors logic
    def select_master():
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if path:
            master_var.set(path)
            nonlocal_master_cols = list(pd.read_excel(path, nrows=0).columns)
            master_cols.clear()
            master_cols.extend(nonlocal_master_cols)
            left_list.delete(0,"end")
            for c in master_cols:
                left_list.insert("end", c)

    def select_folder():
        path = filedialog.askdirectory()
        if path:
            folder_var.set(path)
            for f in os.listdir(path):
                if f.endswith(".xlsx"):
                    nonlocal_target_cols = list(pd.read_excel(os.path.join(path,f), nrows=0).columns)
                    target_cols.clear()
                    target_cols.extend(nonlocal_target_cols)
                    right_list.delete(0,"end")
                    for c in target_cols:
                        right_list.insert("end", c)
                    break

    return win
