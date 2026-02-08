import os
import random
import pandas as pd
import tkinter as tk
import ttkbootstrap as tb
from tkinter import filedialog, messagebox


def open_files_combinations_tool(root):
    """Launch the Files Combinations Tool UI"""

    win = tb.Toplevel(root)
    win.title("Files Combinations Tool")
    win.geometry("800x600")

    state = {
        "df": None,
        "selected_col": None,
        "record_limits": []
    }

    # ------------------------
    # File Import
    # ------------------------
    def load_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx *.xls")]
        )
        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                state["df"] = pd.read_csv(file_path)
            else:
                state["df"] = pd.read_excel(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")
            return

        cols_listbox.delete(0, tk.END)
        for col in state["df"].columns:
            cols_listbox.insert(tk.END, col)

        messagebox.showinfo("Success", f"Loaded file with {len(state['df'])} records.")

    # ------------------------
    # Add Record Limit
    # ------------------------
    def add_limit():
        try:
            val = int(limit_entry.get())
            if val > 0:
                state["record_limits"].append(val)
                limits_listbox.insert(tk.END, f"{val:,} records")
                limit_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showwarning("Invalid", "Enter a valid integer limit.")

    # ------------------------
    # Start Processing
    # ------------------------
    def start_processing():
        if state["df"] is None:
            messagebox.showwarning("No File", "Please load a file first.")
            return

        if not state["selected_col"]:
            messagebox.showwarning("No Column", "Please select a column.")
            return

        if not state["record_limits"]:
            messagebox.showwarning("No Limits", "Please enter at least one record limit.")
            return

        col = state["selected_col"]
        df = state["df"]

        # Folder setup
        base_out = os.path.join(os.getcwd(), "Processed")
        os.makedirs(base_out, exist_ok=True)

        remaining_df = df.copy()

        for limit in state["record_limits"]:
            chosen = remaining_df.sample(min(limit, len(remaining_df)), random_state=42)
            remaining_df = remaining_df.drop(chosen.index)

            folder = os.path.join(base_out, f"{limit}K")
            os.makedirs(folder, exist_ok=True)

            out_file = os.path.join(folder, f"subset_{limit}.csv")
            chosen.to_csv(out_file, index=False)

            txt_file = os.path.join(folder, "records.txt")
            with open(txt_file, "w") as f:
                f.write("\n".join(map(str, chosen[col].tolist())))

        # Save remaining
        if not remaining_df.empty:
            folder = os.path.join(base_out, "Remaining")
            os.makedirs(folder, exist_ok=True)
            out_file = os.path.join(folder, "remaining.csv")
            remaining_df.to_csv(out_file, index=False)

            txt_file = os.path.join(folder, "records.txt")
            with open(txt_file, "w") as f:
                f.write("\n".join(map(str, remaining_df[col].tolist())))

        messagebox.showinfo("Done", f"Processing complete. Results saved in:\n{base_out}")

    # ------------------------
    # UI Layout
    # ------------------------
    frame = tb.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # File Load
    tb.Button(frame, text="Load CSV/Excel File", bootstyle="primary", command=load_file).pack(pady=5)

    # Columns list
    tb.Label(frame, text="Available Columns (select one):").pack()
    cols_listbox = tk.Listbox(frame, height=8, exportselection=False)
    cols_listbox.pack(fill="x", pady=5)

    def on_col_select(event):
        selected = cols_listbox.get(tk.ACTIVE)
        state["selected_col"] = selected

    cols_listbox.bind("<<ListboxSelect>>", on_col_select)

    # Record limits
    limit_frame = tb.Frame(frame)
    limit_frame.pack(fill="x", pady=10)

    limit_entry = tb.Entry(limit_frame)
    limit_entry.pack(side="left", padx=5, expand=True, fill="x")

    tb.Button(limit_frame, text="Add Limit", bootstyle="secondary", command=add_limit).pack(side="left", padx=5)

    limits_listbox = tk.Listbox(frame, height=5)
    limits_listbox.pack(fill="x", pady=5)

    # Start button
    tb.Button(frame, text="Start Combinating", bootstyle="success", command=start_processing).pack(pady=20)
