import pandas as pd
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

class FileMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced File Merger")
        self.root.geometry("900x600")

        # Buttons
        top = tk.Frame(root)
        top.pack(pady=10, fill=tk.X)

        self.select_btn = tk.Button(top, text="Select Folder", command=self.select_folder)
        self.select_btn.pack(side=tk.LEFT, padx=10)

        self.merge_btn = tk.Button(top, text="Merge Files", command=self.merge_files, state=tk.DISABLED)
        self.merge_btn.pack(side=tk.LEFT, padx=10)

        # Treeview for headers
        self.tree = ttk.Treeview(root, columns=("file", "headers", "count"), show="headings")
        self.tree.heading("file", text="File")
        self.tree.heading("headers", text="Headers (Columns)")
        self.tree.heading("count", text="Column Count")

        self.tree.column("file", width=220, anchor="w")
        self.tree.column("headers", width=550, anchor="w")
        self.tree.column("count", width=100, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(root, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.folder_path = None
        self.files = []

    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.folder_path = folder
        self.files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(('.csv', '.xlsx', '.xls'))
        ]

        if not self.files:
            messagebox.showwarning("No Files", "No CSV or Excel files found in this folder!")
            self.merge_btn.config(state=tk.DISABLED)
            return

        self.merge_btn.config(state=tk.NORMAL)
        self.show_headers()

    def show_headers(self):
        # Clear previous
        for row in self.tree.get_children():
            self.tree.delete(row)

        for f in self.files:
            try:
                if f.lower().endswith(".csv"):
                    df = pd.read_csv(f, nrows=0)  # only headers
                else:
                    df = pd.read_excel(f, nrows=0)
                cols = list(df.columns)
            except Exception as e:
                cols = [f"ERROR: {e}"]

            self.tree.insert(
                "",
                "end",
                values=(os.path.basename(f), ", ".join(cols), len(cols))
            )

    def merge_files(self):
        if not self.files:
            return

        dfs = []
        record_counts = {}
        for f in self.files:
            df = pd.read_csv(f) if f.lower().endswith(".csv") else pd.read_excel(f)
            dfs.append(df)
            record_counts[os.path.basename(f)] = len(df)

        merged = pd.concat(dfs, ignore_index=True)

        # Save Excel with plain header (no bold, no border)
        output_xlsx = os.path.join(self.folder_path, "merged_output.xlsx")
        with pd.ExcelWriter(output_xlsx, engine="xlsxwriter") as writer:
            merged.to_excel(writer, index=False, header=False, sheet_name="Sheet1", startrow=1)

            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]
            header_fmt = workbook.add_format({"bold": False, "border": 0})
            for c, name in enumerate(merged.columns):
                worksheet.write(0, c, name, header_fmt)

        # Write records summary
        output_txt = os.path.join(self.folder_path, "Merger Records.txt")
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

        # Open folder
        try:
            if os.name == "nt":
                subprocess.Popen(f'explorer "{self.folder_path}"')
            else:
                subprocess.Popen(["open", self.folder_path])
        except:
            pass

        messagebox.showinfo("Success", f"Saved merged_output.xlsx and Merger Records.txt\nin {self.folder_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileMergerApp(root)
    root.mainloop()
