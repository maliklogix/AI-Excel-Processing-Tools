import pandas as pd
import os
from .helpers import save_excel

def csv_to_excel(file, out_folder):
    # Read all as string to avoid Excel guessing
    df = pd.read_csv(file, dtype=str)
    filename = os.path.splitext(os.path.basename(file))[0] + ".xlsx"

    excel_converted_folder = os.path.join(os.path.dirname(file), 'Excel Converted')
    os.makedirs(excel_converted_folder, exist_ok=True)

    save_excel(df, os.path.join(excel_converted_folder, filename))
    return excel_converted_folder


def excel_to_csv(file, out_folder):
    # Read all as string to preserve formatting (ZIP, codes, etc.)
    df = pd.read_excel(file, dtype=str)
    filename = os.path.splitext(os.path.basename(file))[0] + ".csv"

    csv_converted_folder = os.path.join(os.path.dirname(file), 'CSV Converted')
    os.makedirs(csv_converted_folder, exist_ok=True)

    df.to_csv(os.path.join(csv_converted_folder, filename), index=False)
    return csv_converted_folder
