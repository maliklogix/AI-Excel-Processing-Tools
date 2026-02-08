# ======================================================================
#                        IMPORTS & CONFIG
# ======================================================================
import os
import re
import shutil
import zipfile
import pandas as pd

# ---------- CONFIG (Script 01) ----------
TXT_NAME = "List Building Records.txt"
TARGET_COL = "List"  # the column we count for "All Records (List)"

# Map of acceptable key variants in the TXT -> normalized key used in output
KEY_ALIASES = {
    "2BSKIP": "2BSkip",
    "2B SKIP": "2BSkip",
    "CCREADY": "CC Ready",
    "CC READY": "CC Ready",
    "GHLREADY": "GHL Ready",
    "GHL READY": "GHL Ready",
    "SCREADY": "SC Ready",
    "SC READY": "SC Ready",
    "SKIPTRACED": "SkipTraced",
    "SKIP TRACED": "SkipTraced",
    "NO HIT FILE": "No Hit File",
    "NO HIT": "No Hit File",
    "NOHIT": "No Hit File",
    "NOHITFILE": "No Hit File",
}

# Regex to capture "Key : 123" or "Key: 1,234" with optional quotes after key
VALUE_RE = re.compile(r"""^(.+?)['"]?\s*:\s*([0-9,]+)\s*$""")


# ======================================================================
#                        SCRIPT 01 – Extract TXT + CSV Summary
# ======================================================================
def parse_txt_counts(txt_path):
    # Initialize with all possible keys including "No Hit File"
    all_keys = set(KEY_ALIASES.values())
    results = {v: 0 for v in all_keys}
    if not os.path.exists(txt_path):
        return results

    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
    except Exception:
        return results

    for line in lines:
        m = VALUE_RE.match(line.strip())
        if not m:
            continue
        raw_key, raw_val = m.groups()
        key_norm = re.sub(r"\s+", " ", raw_key).strip().upper()
        key_norm = KEY_ALIASES.get(key_norm, None)
        if not key_norm:
            continue
        try:
            num = int(str(raw_val).replace(",", "").strip())
        except ValueError:
            num = 0
        results[key_norm] = num
    return results


def count_all_records_in_csv(csv_path, target_col=TARGET_COL):
    try:
        try:
            df = pd.read_csv(csv_path)
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding="latin-1")

        wanted = None
        for c in df.columns:
            if str(c).strip().lower() == target_col.strip().lower():
                wanted = c
                break
        if wanted is None:
            return 0, f"Column '{target_col}' not found"

        series = df[wanted]
        non_empty = series.dropna()
        if non_empty.dtype == object:
            non_empty = non_empty.map(lambda x: str(x).strip()).replace("", pd.NA).dropna()
        return int(non_empty.shape[0]), "OK"
    except Exception as e:
        return 0, f"Error reading CSV: {e}"


def collect_data_script1(base_dir, out_dir):
    rows = []
    for root, dirs, files in os.walk(base_dir):
        if os.path.abspath(root).startswith(os.path.abspath(out_dir)):
            continue

        folder_name = os.path.basename(root)
        txt_path = os.path.join(root, TXT_NAME)
        txt_exists = os.path.exists(txt_path)
        txt_counts = parse_txt_counts(txt_path) if txt_exists else {v: 0 for v in set(KEY_ALIASES.values())}

        csv_files = [f for f in files if f.lower().endswith(".csv") and not f.startswith("~$")]
        for csv_name in csv_files:
            csv_path = os.path.join(root, csv_name)
            total_records, note = count_all_records_in_csv(csv_path, TARGET_COL)
            rows.append({
                "List Name": folder_name,
                "2BSkip": txt_counts.get("2BSkip", 0),
                "CC Ready": txt_counts.get("CC Ready", 0),
                "GHL Ready": txt_counts.get("GHL Ready", 0),
                "SC Ready": txt_counts.get("SC Ready", 0),
                "SkipTraced": txt_counts.get("SkipTraced", 0),
                "No Hit File": txt_counts.get("No Hit File", 0),
                "All Records (List)": total_records,
                "Notes": note if note != "OK" else "",
            })

        if txt_exists and not csv_files:
            rows.append({
                "List Name": folder_name,
                "2BSkip": txt_counts.get("2BSkip", 0),
                "CC Ready": txt_counts.get("CC Ready", 0),
                "GHL Ready": txt_counts.get("GHL Ready", 0),
                "SC Ready": txt_counts.get("SC Ready", 0),
                "SkipTraced": txt_counts.get("SkipTraced", 0),
                "No Hit File": txt_counts.get("No Hit File", 0),
                "All Records (List)": 0,
                "Notes": "TXT found; no CSV in folder",
            })
    return rows


def run_script1():
    base_dir = os.getcwd()
    out_dir = os.path.join(base_dir, "Data pulling records")
    out_file = os.path.join(out_dir, "Extracted_Records.xlsx")
    
    os.makedirs(out_dir, exist_ok=True)
    rows = collect_data_script1(base_dir, out_dir)
    if not rows:
        print("No matching CSV/TXT files found.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Add a total row at the end
    total_row = {
        "List Name": "TOTAL",
        "2BSkip": df["2BSkip"].sum(),
        "CC Ready": df["CC Ready"].sum(),
        "GHL Ready": df["GHL Ready"].sum(),
        "SC Ready": df["SC Ready"].sum(),
        "SkipTraced": df["SkipTraced"].sum(),
        "No Hit File": df["No Hit File"].sum(),
        "All Records (List)": df["All Records (List)"].sum(),
        "Notes": ""
    }
    
    # Append the total row to the DataFrame
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    
    # Define column order
    ordered_cols = [
        "List Name", "2BSkip", "CC Ready", "GHL Ready", "SC Ready", "SkipTraced", "No Hit File",
        "All Records (List)", "Notes"
    ]
    
    # Ensure all columns are included
    for c in df.columns:
        if c not in ordered_cols:
            ordered_cols.append(c)
    
    df = df[ordered_cols]
    
    # Write to Excel
    with pd.ExcelWriter(out_file, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Summary")
        
        # Get the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets["Summary"]
        
        # Add a bold format for the total row
        bold_format = workbook.add_format({"bold": True})
        
        # Apply bold format to the total row
        last_row = len(df)
        for col_num, col_name in enumerate(ordered_cols):
            worksheet.write(last_row, col_num, df.iloc[-1][col_name], bold_format)
    
    print(f"✅ Script1: Data saved to {out_file}")


# ======================================================================
#                        SCRIPT 02 – Collect GHL Ready & Zip
# ======================================================================
def extract_info_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    skiptraced = re.search(r"SkipTraced['\"]?\s*:\s*([0-9,]+)", text)
    scready = re.search(r"SC Ready['\"]?\s*:\s*([0-9,]+)", text)
    nohit = re.search(r"No Hit File['\"]?\s*:\s*([0-9,]+)", text)
    return (
        (skiptraced.group(1) if skiptraced else "0").strip(), 
        (scready.group(1) if scready else "0").strip(),
        (nohit.group(1) if nohit else "0").strip()
    )


def run_script2():
    base_path = os.getcwd()
    output_folder = os.path.join(base_path, "Data pulling records")
    ghl_output_folder = os.path.join(base_path, "Collected GHL Ready Files")
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(ghl_output_folder, exist_ok=True)

    data, zip_name = [], None
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path):
            parts = folder.split("-")
            if len(parts) >= 4:
                week, state = parts[0], parts[-1]
                zip_name = f"{week}-{state}"
            file_path = os.path.join(folder_path, "List Building Records.txt")
            if os.path.exists(file_path):
                skiptraced, scready, nohit = extract_info_from_file(file_path)
                data.append({
                    "Folder Name": folder, 
                    "SkipTraced": skiptraced, 
                    "SC Ready": scready,
                    "No Hit File": nohit
                })
            ghl_folder = os.path.join(folder_path, "GHL Ready")
            if os.path.isdir(ghl_folder):
                for file_name in os.listdir(ghl_folder):
                    src_file = os.path.join(ghl_folder, file_name)
                    if os.path.isfile(src_file):
                        shutil.copy2(src_file, os.path.join(ghl_output_folder, f"{file_name}"))

    csv_file = os.path.join(output_folder, "GHL_Summary.csv")
    if data:
        df = pd.DataFrame(data)
        df.to_csv(csv_file, index=False)
        # print(f"✅ Script2: Data saved to {csv_file}")
    else:
        print("⚠️ Script2: No List Building Records found.")

    print(f"✅ Script2: GHL Ready files copied to {ghl_output_folder}")
    if zip_name:
        zip_file_path = os.path.join(base_path, f"{zip_name}.zip")
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            if csv_file and os.path.exists(csv_file):
                zipf.write(csv_file, os.path.basename(csv_file))
            for root, dirs, files in os.walk(ghl_output_folder):
                for f in files:
                    full_path = os.path.join(root, f)
                    arcname = os.path.basename(full_path)
                    zipf.write(full_path, arcname)
        print(f"✅ Script2: Zip created {zip_file_path}")
    else:
        print("⚠️ Script2: Could not determine zip name.")


# ======================================================================
#                        SCRIPT 03 – Folder Organization
# ======================================================================
def organize_folders(base_dir):
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            parts = folder.split('-')
            if len(parts) < 4:
                continue
            week, year, absentee, city, state = parts[0], parts[1], parts[2], parts[-2], parts[-1]
            state_dir = os.path.join(base_dir, state)
            city_dir = os.path.join(state_dir, city)
            week_dir = os.path.join(city_dir, week)
            absentee_dir = os.path.join(week_dir, absentee)
            for d in [state_dir, city_dir, week_dir, absentee_dir]:
                os.makedirs(d, exist_ok=True)
            for item in os.listdir(folder_path):
                shutil.move(os.path.join(folder_path, item), os.path.join(absentee_dir, item))
            shutil.rmtree(folder_path, ignore_errors=True)

    for root, dirs, files in os.walk(base_dir, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)

    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(".txt"):
                os.remove(os.path.join(root, f))


def run_script3():
    cwd = os.getcwd()
    organize_folders(cwd)
    print("✅ Script3: Organization complete (folders structured, empty dirs removed, .txt files deleted).")


# ======================================================================
#                        MASTER EXECUTION (for standalone use)
# ======================================================================
if __name__ == "__main__":
    run_script1()
    run_script2()
    run_script3()