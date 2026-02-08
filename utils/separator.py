import pandas as pd
import os
import logging
from datetime import datetime
import re

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def save_excel(df, filepath, index=False):
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=index)
        worksheet = writer.sheets['Sheet1']
        for col_num, _ in enumerate(df.columns, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.font = cell.font.copy(bold=False)
            cell.border = None
            cell.fill = None

def _clean_filename(filename):
    """Only remove illegal characters for OS. Do NOT change spaces or dashes."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    filename = ''.join(c for c in filename if ord(c) >= 32)
    filename = filename.strip()
    return filename[:100]

def separate_by_column(file, column, output_dir=None, file_format='xlsx',
                      include_index=False, max_files=None, custom_naming=None,
                      handle_na='skip', na_label='Unknown'):

    if file_format not in ['xlsx', 'csv', 'both']:
        raise ValueError("file_format must be 'xlsx', 'csv', or 'both'")
    if handle_na not in ['skip', 'include', 'separate']:
        raise ValueError("handle_na must be 'skip', 'include', or 'separate'")

    if output_dir is None:
        input_dir = os.path.dirname(file)
        output_dir = os.path.join(input_dir, "Separated_Files")
    ensure_folder(output_dir)

    # Read file
    if file.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    # Handle NaN values
    if handle_na == 'skip':
        df = df.dropna(subset=[column] if isinstance(column, str) else column)
    elif handle_na in ['include', 'separate']:
        df = df.fillna({col: na_label for col in ([column] if isinstance(column, str) else column)})

    # Multi-column grouping
    if isinstance(column, list):
        df['_group_key'] = df[column].astype(str).agg(' '.join, axis=1)
    else:
        df['_group_key'] = df[column]

    file_records = {}
    total_records = 0

    # Separate files
    for value, group in df.groupby('_group_key'):
        filename_base = custom_naming(value) if custom_naming else _clean_filename(str(value))
        files_created = []

        if file_format in ['xlsx', 'both']:
            excel_file = os.path.join(output_dir, f"{filename_base}.xlsx")
            save_excel(group.drop(columns=['_group_key']), excel_file, index=include_index)
            files_created.append(excel_file)

        if file_format in ['csv', 'both']:
            csv_file = os.path.join(output_dir, f"{filename_base}.csv")
            group.drop(columns=['_group_key']).to_csv(csv_file, index=include_index)
            files_created.append(csv_file)

        file_records[filename_base] = len(group)
        total_records += len(group)

    # Save summary as TXT
    summary_txt = os.path.join(output_dir, "separation_summary.txt")
    with open(summary_txt, 'w') as f:
        for fname, count in file_records.items():
            f.write(f"{fname} = {count}\n")
        f.write(f"\nTotal Records = {total_records}\n")

    logger.info(f"Separated {file} into {len(file_records)} files. Total records: {total_records}")
    return file_records
