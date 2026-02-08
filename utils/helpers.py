import os
import pandas as pd

def ensure_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def save_excel(df, filepath):
    df_to_save = df.fillna("")
    ensure_folder(os.path.dirname(filepath))
    with pd.ExcelWriter(filepath, engine="xlsxwriter") as writer:
        df_to_save.to_excel(writer, sheet_name="Sheet1", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        fmt = workbook.add_format({"border": 0})
        for col, val in enumerate(df_to_save.columns):
            worksheet.write(0, col, val, fmt)
