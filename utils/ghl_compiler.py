import pandas as pd
import os
from .helpers import ensure_folder

def step_05_reshape(df):
    def extract_numeric_phone(phone):
        # keep phone values exactly as they come from step_04
        return phone  

    # find phone columns
    phone_cols = [col for col in df.columns if col.lower().startswith("phone")]

    output_rows = []
    for _, row in df.iterrows():
        # collect valid phones
        phone_numbers = []
        for phone_col in phone_cols:
            val = row.get(phone_col, None)
            if pd.notna(val) and str(val).strip() != "" and str(val).strip().lower() not in ["nan", "none", "null", "0"]:
                phone_numbers.append(extract_numeric_phone(val))

        # 🔥 skip rows with no phone numbers
        if not phone_numbers:
            continue

        # expand multiple phones into separate rows
        for phone in phone_numbers:
            new_row = {}
            for col in df.columns:
                if col in phone_cols:
                    continue  # skip original phone cols
                new_row[col] = row.get(col, "")
            new_row["Phone"] = phone
            output_rows.append(new_row)

    reshaped = pd.DataFrame(output_rows)

    # 🔎 Reorder columns
    cols = list(reshaped.columns)

    if "Email" in cols:
        # place Phone right before Email
        cols.remove("Phone")
        email_index = cols.index("Email")
        cols.insert(email_index, "Phone")
    else:
        # if no Email, keep Phone at the end
        cols = [c for c in cols if c != "Phone"] + ["Phone"]

    reshaped = reshaped[cols]

    return reshaped


def run_step05_pipeline(input_file):
    # get file name and directory
    name = os.path.splitext(os.path.basename(input_file))[0]
    input_dir = os.path.dirname(input_file)

    # read input
    df = pd.read_csv(input_file) if input_file.endswith(".csv") else pd.read_excel(input_file)

    # reshape
    reshaped = step_05_reshape(df)

    # 🔥 create output folder inside input file's directory
    folder = os.path.join(input_dir, "GHL Ready in CSV")
    ensure_folder(folder)

    # save as CSV
    out_path = os.path.join(folder, f"{name}.csv")
    reshaped.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"✅ Saved CSV: {out_path}")
