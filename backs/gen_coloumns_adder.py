# utils/gen_coloumns_adder.py
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as tb

# -----------------------------
# Apply column addition
# -----------------------------
def apply_column_addition(master_file, folder, mappings):
    try:
        master_df = pd.read_excel(master_file, dtype=str)

        for root, _, files in os.walk(folder):
            for file in files:
                if not file.endswith(".xlsx"):
                    continue
                file_path = os.path.join(root, file)
                df = pd.read_excel(file_path, dtype=str)

                # Process each mapping
                for m in mappings:
                    master_col, folder_col, new_col, insert_after = m

                    # Build mapping dictionary from master
                    if master_col not in master_df.columns:
                        continue
                    map_dict = dict(zip(master_df[master_col], master_df[new_col] if new_col in master_df.columns else master_df[master_col]))

                    # Fill values
                    if folder_col in df.columns:
                        df[new_col] = df[folder_col].map(map_dict)

                        # Reorder if insert_after provided
                        if insert_after and insert_after in df.columns:
                            cols = list(df.columns)
                            cols.remove(new_col)
                            pos = cols.index(insert_after) + 1
                            cols.insert(pos, new_col)
                            df = df[cols]

                df.to_excel(file_path, index=False)
        messagebox.showinfo("✅ Success", f"Columns added into files in {folder}")
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed: {e}")


# -----------------------------
# Dashboard UI
# -----------------------------
def run_column_adder(root):
    win = tb.Toplevel(root)
    win.title("Column Adder Dashboard")
    win.geometry("1000x700")
    win.configure(bg="#fff8f0")

    master_var = tk.StringVar()
    folder_var = tk.StringVar()
    mappings = []

    # --- Selectors
    def browse_master():
        file = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if file:
            master_var.set(file)
            load_columns()

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            folder_var.set(folder)
            load_columns()

    frame_top = tb.Frame(win)
    frame_top.pack(fill="x", pady=8)

    tb.Label(frame_top, text="Master File:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=4)
    tb.Entry(frame_top, textvariable=master_var, width=50).pack(side="left", padx=4)
    tb.Button(frame_top, text="Browse", command=browse_master).pack(side="left", padx=4)

    tb.Label(frame_top, text="   Folder:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=4)
    tb.Entry(frame_top, textvariable=folder_var, width=40).pack(side="left", padx=4)
    tb.Button(frame_top, text="Browse", command=browse_folder).pack(side="left", padx=4)

    # --- Column lists
    frame_lists = tb.Frame(win)
    frame_lists.pack(fill="both", expand=True, padx=10, pady=10)

    master_cols = tk.Listbox(frame_lists, selectmode="browse", width=40, height=20, exportselection=False)
    folder_cols = tk.Listbox(frame_lists, selectmode="browse", width=40, height=20, exportselection=False)

    tb.Label(frame_lists, text="Master Columns", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, pady=5)
    tb.Label(frame_lists, text="Folder Columns", font=("Segoe UI", 12, "bold")).grid(row=0, column=1, pady=5)

    master_cols.grid(row=1, column=0, padx=10)
    folder_cols.grid(row=1, column=1, padx=10)

    # --- Mapping table
    table_frame = tb.Frame(win, bootstyle="light")
    table_frame.pack(fill="both", expand=True, pady=10, padx=10)

    cols = ("master", "folder", "newcol", "insert_after")
    tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=6)
    for c in cols:
        tree.heading(c, text=c.title())
        tree.column(c, width=180, anchor="center")
    tree.pack(fill="both", expand=True, side="left")

    sb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.pack(side="right", fill="y")

    # --- Drag-and-drop mapping
    def map_selected():
        try:
            m_idx = master_cols.curselection()[0]
            f_idx = folder_cols.curselection()[0]
            m_name = master_cols.get(m_idx)
            f_name = folder_cols.get(f_idx)

            newcol = tk.simpledialog.askstring("New Column Name", f"Enter new column name for mapping {m_name} == {f_name}:")
            insert_after = tk.simpledialog.askstring("Insert After", "Insert after which column? (leave blank for end):")

            if newcol:
                tree.insert("", "end", values=(m_name, f_name, newcol, insert_after))
                mappings.append((m_name, f_name, newcol, insert_after))
        except:
            messagebox.showerror("Error", "Select one master and one folder column to map.")

    tb.Button(win, text="Map Selected ➡️", bootstyle="primary", command=map_selected).pack(pady=6)

    # --- Run
    def run():
        if not master_var.get() or not folder_var.get():
            messagebox.showerror("❌ Error", "Please select both master file and folder.")
            return
        if not mappings:
            messagebox.showerror("❌ Error", "Please create at least one mapping.")
            return
        apply_column_addition(master_var.get(), folder_var.get(), mappings)

    tb.Button(win, text="Run Column Addition", bootstyle="success", command=run).pack(pady=12)

    # --- Load columns
    def load_columns():
        master_cols.delete(0, tk.END)
        folder_cols.delete(0, tk.END)
        try:
            if master_var.get():
                dfm = pd.read_excel(master_var.get(), nrows=0)
                for c in dfm.columns:
                    master_cols.insert(tk.END, c)
            if folder_var.get():
                # get first Excel file inside folder
                for f in os.listdir(folder_var.get()):
                    if f.endswith(".xlsx"):
                        dff = pd.read_excel(os.path.join(folder_var.get(), f), nrows=0)
                        for c in dff.columns:
                            folder_cols.insert(tk.END, c)
                        break
        except Exception as e:
            messagebox.showerror("Error", f"Could not load columns: {e}")

    return win
