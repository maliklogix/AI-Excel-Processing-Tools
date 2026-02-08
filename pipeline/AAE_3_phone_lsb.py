import pandas as pd
import os
import re
from datetime import datetime

# -------------------------
# Utilities
# -------------------------
def to_pascal_case(text):
    if pd.isna(text):
        return text
    return ' '.join(word.capitalize() for word in str(text).split())

def normalize_address(addr):
    if pd.isna(addr):
        return ""
    addr = str(addr).strip().lower()
    addr = re.sub(r"\s+", " ", addr)
    return addr

def ensure_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def extract_email_column(df):
    """
    Find and extract email column from input dataframe.
    Looks for columns containing 'email' (case insensitive).
    Returns the email column name and data if found.
    """
    email_columns = [col for col in df.columns if 'email' in str(col).lower()]
    
    if email_columns:
        # Use the first email column found
        email_col = email_columns[0]
        return email_col, df[email_col].copy()
    
    return None, pd.Series([pd.NA] * len(df))

# -------------------------
# Tracking and Logging Functions
# -------------------------
def initialize_tracking_log(output_folder, list_name):
    """Initialize a tracking log file for a specific list"""
    tracker_folder = os.path.join(output_folder, list_name)
    ensure_folder(tracker_folder)
    
    tracker_path = os.path.join(tracker_folder, f"{list_name}_processing_tracker.txt")
    
    with open(tracker_path, 'w') as f:
        f.write(f"AAE 3 Phone LSB Processing Tracker - {list_name}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Processing started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
    
    return tracker_path

def log_processing_step(tracker_path, step_name, record_count, file_path=None, details=""):
    """Log a processing step to the tracking file"""
    with open(tracker_path, 'a') as f:
        timestamp = datetime.now().strftime('%H:%M:%S')
        f.write(f"[{timestamp}] {step_name}: {record_count} records")
        if file_path:
            f.write(f" -> {os.path.basename(file_path)}")
        if details:
            f.write(f" ({details})")
        f.write("\n")

def finalize_tracking_log(tracker_path, total_steps, success=True):
    """Finalize the tracking log with summary"""
    with open(tracker_path, 'a') as f:
        f.write("\n" + "=" * 60 + "\n")
        status = "COMPLETED SUCCESSFULLY" if success else "COMPLETED WITH ERRORS"
        f.write(f"Processing {status}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total processing steps: {total_steps}\n")
        f.write("=" * 60 + "\n")

def create_summary_tracker(output_folder, all_trackers):
    """Create a summary tracker for all processed lists"""
    summary_path = os.path.join(output_folder, "AAE_Processing_Summary.txt")
    
    with open(summary_path, 'w') as f:
        f.write("AAE 3 Phone LSB Processing Summary\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        for list_name, tracker_data in all_trackers.items():
            f.write(f"LIST: {list_name}\n")
            f.write("-" * 40 + "\n")
            
            for step, count in tracker_data.items():
                f.write(f"{step}: {count} records\n")
            
            f.write("\n")
    
    print(f"📊 Summary tracker created: {summary_path}")
    return summary_path

# -------------------------
# STEP 01: Clean + standardize (split Owner Name => First/Last)
# -------------------------
def step_01_clean_and_standardize(df, list_name, tracker_path=None):
    # Extract email data if available
    email_col_name, email_data = extract_email_column(df)
    
    # If Owner Name exists, split into First Name + Last Name
    if "Owner Name" in df.columns:
        df["Owner Name"] = df["Owner Name"].astype(str).str.strip()
        df["First Name"] = df["Owner Name"].apply(lambda x: x.split(" ", 1)[0] if x else "")
        df["Last Name"] = df["Owner Name"].apply(lambda x: x.split(" ", 1)[1] if " " in x else "")

    cleaned = df.rename(columns={
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'associated_property_address_line_1': 'Property Address',
        'associated_property_address_city': 'Property City',
        'associated_property_address_state': 'Property State',
        'associated_property_address_zipcode': 'Property Zip',
        'primary_mailing_address': 'Mailing Address',
        'primary_mailing_city': 'Mailing City',
        'primary_mailing_state': 'Mailing State',
        'primary_mailing_zip': 'Mailing Zip',
        'phone_1': 'Phone1',
        'phone_2': 'Phone2',
        'phone_3': 'Phone3',
        'phone_1_type': 'Type1',
        'phone_2_type': 'Type2',
        'phone_3_type': 'Type3'
    })

    # Ensure Pascal case for mailing address/city (harmless if NaN)
    if 'Mailing Address' in cleaned.columns:
        cleaned['Mailing Address'] = cleaned['Mailing Address'].apply(to_pascal_case)
    if 'Mailing City' in cleaned.columns:
        cleaned['Mailing City'] = cleaned['Mailing City'].apply(to_pascal_case)

    columns_to_keep = [
        'First Name', 'Last Name',
        'Property Address', 'Property City', 'Property State', 'Property Zip',
        'Mailing Address', 'Mailing City', 'Mailing State', 'Mailing Zip',
        'Phone1', 'Type1', 'Phone2', 'Type2', 'Phone3', 'Type3'
    ]

    # Add missing expected columns as pd.NA so selecting doesn't error
    for c in columns_to_keep:
        if c not in cleaned.columns:
            cleaned[c] = pd.NA

    cleaned = cleaned[columns_to_keep]
    
    # Add email column before 'List'
    cleaned['Email'] = email_data.reset_index(drop=True) if not email_data.empty else pd.NA
    cleaned['List'] = list_name
    
    # Log this step
    if tracker_path:
        log_processing_step(tracker_path, "Step 01 - Cleaned and Standardized", len(cleaned), 
                           details=f"Input: {len(df)} records")
    
    return cleaned

# -------------------------
# STEP 02: Remove phones (creates 2BSkip output)
# -------------------------
def step_02_remove_phones(df, tracker_path=None):
    result = df.drop(columns=['Phone1', 'Type1', 'Phone2', 'Type2', 'Phone3', 'Type3','Email'], errors='ignore')
    
    # Log this step
    if tracker_path:
        log_processing_step(tracker_path, "Step 02 - Phones Removed (2BSkip)", len(result))
    
    return result

# -------------------------
# STEP 03: Dedupe + No Hit extraction
def remove_type_columns_from_cc_ready(file_path):
    """
    Remove Type1–Type6 columns from CC Ready files but KEEP Email
    """
    try:
        df = pd.read_excel(file_path)
        # Remove Type columns
        columns_to_remove = ['Type1', 'Type2', 'Type3']
        df = df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors='ignore')

        # Save back
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)

        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        no_border_format = workbook.add_format({'border': 0})

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, no_border_format)

        writer.close()
        print(f"✅ Removed Type columns from: {file_path}")
        return df

    except Exception as e:
        print(f"❌ Error processing CC Ready file: {str(e)}")
        return None

# -------------------------
def step_03_dedupe_and_cleanup(df, list_name, output_folder=None, tracker_path=None):
    initial_count = len(df)
    df = df.drop_duplicates()
    after_dedupe = len(df)
    
    df['normalized_address'] = df['Property Address'].apply(normalize_address)
    df = df.drop_duplicates(subset=['normalized_address'])
    after_address_dedupe = len(df)
    df = df.drop(columns=['normalized_address'], errors='ignore')

    mask_no_phones = df[['Phone1', 'Phone2', 'Phone3']].isna().all(axis=1)
    df_no_hit = df[mask_no_phones].copy()

    if not df_no_hit.empty and output_folder:
        no_hit_folder = os.path.join(output_folder, "No Hit")
        ensure_folder(no_hit_folder)
        no_hit_path = os.path.join(no_hit_folder, f"{list_name}.xlsx")

        with pd.ExcelWriter(no_hit_path, engine='xlsxwriter') as writer:
            df_no_hit.to_excel(writer, sheet_name='Sheet1', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            no_border_format = workbook.add_format({'border': 0})

            # header row
            for col_num, value in enumerate(df_no_hit.columns.values):
                worksheet.write(0, col_num, value, no_border_format)
            # data rows
            for row_num in range(1, len(df_no_hit) + 1):
                for col_num in range(len(df_no_hit.columns)):
                    value = df_no_hit.iloc[row_num - 1, col_num]
                    worksheet.write(row_num, col_num, "" if pd.isna(value) else value, no_border_format)

        print(f"📂 No Hit file created at: {no_hit_path}")
        
        # Log No Hit records
        if tracker_path:
            log_processing_step(tracker_path, "Step 03 - No Hit Records", len(df_no_hit), no_hit_path)

    # Keep rows that have at least one of Phone1..Phone3
    df = df[~mask_no_phones].copy()

    # Insert Phone4/Phone5 placeholders near the List column position (keeps compatibility)
    if 'List' in df.columns:
        insert_pos = df.columns.get_loc('List')
    else:
        insert_pos = len(df.columns)
    df.insert(insert_pos, 'Phone4', pd.NA)
    df.insert(insert_pos, 'Phone5', pd.NA)

    df['List'] = list_name
    
    # Log this step
    if tracker_path:
        details = f"Duplicates removed: {initial_count - after_dedupe}, Address duplicates: {after_dedupe - after_address_dedupe}"
        log_processing_step(tracker_path, "Step 03 - Deduplicated (CC Ready)", len(df), details=details)
    
    return df

# -------------------------
# STEP 03.5: Process Step03 File (CC Ready) - Remove Type columns and swap Phone4/Phone5
# -------------------------
def process_step03_file(file_path, tracker_path=None):
    """
    Process Step03 File (CC Ready): Remove Type, Type1, Type2, Type3 columns,
    then rename Phone4 to Phone5 and Phone5 to Phone4, and ensure Email column is before List
    """
    try:
        # Read the Step03 file
        df = pd.read_excel(file_path)
        initial_count = len(df)
        
        # Rename Phone4 to Phone5 and Phone5 to Phone4 (swap the columns)
        if 'Phone4' in df.columns and 'Phone5' in df.columns:
            df = df.rename(columns={'Phone4': 'Phone5_temp', 'Phone5': 'Phone4'})
            df = df.rename(columns={'Phone5_temp': 'Phone5'})
        elif 'Phone4' in df.columns:
            df = df.rename(columns={'Phone4': 'Phone5'})
        elif 'Phone5' in df.columns:
            df = df.rename(columns={'Phone5': 'Phone4'})
        
        # Ensure Email column is before List column
        if 'Email' in df.columns and 'List' in df.columns:
            # Get current column order
            columns = list(df.columns)
            
            # Remove Email from current position
            columns.remove('Email')
            
            # Find List position and insert Email before it
            list_index = columns.index('List')
            columns.insert(list_index, 'Email')
            
            # Reorder dataframe
            df = df[columns]
        
        # Save the processed file back (overwrite original)
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            no_border_format = workbook.add_format({'border': 0})
            
            # Format header row
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, no_border_format)
            
            # Format data rows
            for row_num in range(1, len(df) + 1):
                for col_num in range(len(df.columns)):
                    value = df.iloc[row_num - 1, col_num]
                    worksheet.write(row_num, col_num, "" if pd.isna(value) else value, no_border_format)
        
        print(f"✅ Processed Step03 file: {file_path}")
        
        # Log this step
        if tracker_path:
            log_processing_step(tracker_path, "Step 03.5 - CC Ready Processed", len(df), file_path)
        
        return df
        
    except Exception as e:
        print(f"❌ Error processing Step03 file: {str(e)}")
        return None

# -------------------------
# STEP 04: Remove landlines (only where TypeX == 'Landline')
# -------------------------
def step_04_remove_landlines(df, tracker_path=None):
    initial_count = len(df)
    
    # Ensure Phone1..Phone3 exist (like before)
    for i in range(1, 4):
        phone_col = f'Phone{i}'
        type_col = f'Type{i}'

        if phone_col not in df.columns:
            df[phone_col] = pd.NA
        if type_col not in df.columns:
            df[type_col] = pd.NA

        # Remove ONLY landlines
        mask_landline = (
            df[type_col]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("landline")
        )
        df.loc[mask_landline, phone_col] = pd.NA

    # Drop Type columns (same as before)
    df = df.drop(columns=['Type1', 'Type2', 'Type3'], errors='ignore')

    # Keep rows with at least one phone (Phone1..Phone3)
    df = df[df[['Phone1', 'Phone2', 'Phone3']].notna().any(axis=1)].copy()
    after_landline_removal = len(df)

    # Drop placeholder Phone4/Phone5 before next steps
    df = df.drop(columns=['Phone4', 'Phone5'], errors='ignore')
    
    # Log this step
    if tracker_path:
        landlines_removed = initial_count - after_landline_removal
        log_processing_step(tracker_path, "Step 04 - Landlines Removed (SC Ready)", len(df), 
                           details=f"Landlines removed: {landlines_removed}")

    return df

# -------------------------
# STEP 05: Reshape for GHL - ALWAYS use PROPERTY columns
# -------------------------
def step_05_reshape(df, tracker_path=None):
    def extract_numeric_phone(phone):
        if pd.isna(phone):
            return None
        phone = re.sub(r'\D', '', str(phone))
        if phone.endswith("0"):
            phone = phone[:-1]
        return int(phone) if phone.isdigit() else None

    output_rows = []
    for _, row in df.iterrows():
        first_name = row.get("First Name", "")
        last_name = row.get("Last Name", "")
        email = row.get("Email", "")  # Get email from row

        # ✅ Force Property columns (ignore Mailing)
        address = row.get("Property Address", "")
        city = row.get("Property City", "")
        state = row.get("Property State", "")
        zip_code = row.get("Property Zip", "")
        list_val = row.get("List", "")

        phone_numbers = []
        for phone_col in ["Phone1", "Phone2", "Phone3"]:
            if phone_col in row:
                cleaned_phone = extract_numeric_phone(row[phone_col])
                if cleaned_phone:
                    phone_numbers.append(cleaned_phone)

        if not phone_numbers:
            output_rows.append({
                "First Name": first_name,
                "Last Name": last_name,
                
                "Property Address": address,
                "Property City": city,
                "Property State": state,
                "Property Zip": zip_code,
                "Phone": pd.NA,
                "Email": email,  # Include email
                "List": list_val
            })
        else:
            for phone in phone_numbers:
                output_rows.append({
                    "First Name": first_name,
                    "Last Name": last_name,
                  
                    "Property Address": address,
                    "Property City": city,
                    "Property State": state,
                    "Property Zip": zip_code,
                    "Phone": phone,
                    "Email": email,  # Include email
                    "List": list_val
                })

    df_out = pd.DataFrame(output_rows)

    # Drop duplicate phones
    if "Phone" in df_out.columns:
        initial_phones = len(df_out)
        df_out = df_out.drop_duplicates(subset=["Phone"], keep="first")
        duplicates_removed = initial_phones - len(df_out)
    else:
        duplicates_removed = 0
    
    # Log this step
    if tracker_path:
        details = f"Phone duplicates removed: {duplicates_removed}" if duplicates_removed > 0 else ""
        log_processing_step(tracker_path, "Step 05 - Reshaped for GHL", len(df_out), details=details)
    
    return df_out

# -------------------------
# SAVE helper
# -------------------------
def save_to_folder(df, folder, list_name, suffix="", tracker_path=None):
    ensure_folder(folder)
    filepath = os.path.join(folder, f"{list_name}{suffix}.xlsx")
    df_to_save = df.fillna('')

    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        df_to_save.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        no_border_format = workbook.add_format({'border': 0})

        for col_num, value in enumerate(df_to_save.columns.values):
            worksheet.write(0, col_num, value, no_border_format)

        for row_num in range(1, len(df_to_save) + 1):
            for col_num in range(len(df_to_save.columns)):
                worksheet.write(row_num, col_num, df_to_save.iloc[row_num - 1, col_num], no_border_format)

    print(f"✅ Saved: {filepath} ({len(df)} records)")
    
    # Log this save operation
    if tracker_path:
        step_name = os.path.basename(folder)
        log_processing_step(tracker_path, f"Saved to {step_name}", len(df), filepath)
    
    return filepath

# -------------------------
# RUN pipeline for AAE 3 Phone LSB
# -------------------------
def run_aae_pipeline(input_path, list_name, output_folder, is_step01_file=False):
    # Initialize tracking for this list
    tracker_path = initialize_tracking_log(output_folder, list_name)
    log_processing_step(tracker_path, "Pipeline Started", 0, details=f"Input: {os.path.basename(input_path)}")
    
    # Create individual output folder for this specific list
    individual_output_folder = os.path.join(output_folder, list_name)
    ensure_folder(individual_output_folder)
    
    step01_folder = os.path.join(individual_output_folder, "SkipTraced")
    filepath_01 = os.path.join(step01_folder, f"{list_name}.xlsx")
    
    # If input is already a Step01 file, use it directly
    if is_step01_file:
        print(f"Using existing Step01 file: {input_path}")
        df_01 = pd.read_excel(input_path)
        save_to_folder(df_01, step01_folder, list_name, tracker_path=tracker_path)
    else:
        # Check if Step01 file already exists
        if os.path.exists(filepath_01):
            print(f"Found existing step01 file: {filepath_01}. Loading it instead of reprocessing.")
            df_01 = pd.read_excel(filepath_01)
            log_processing_step(tracker_path, "Loaded existing Step01 file", len(df_01), filepath_01)
        else:
            print(f"No existing step01 file found. Processing from raw file: {input_path}")
            # Handle both CSV and Excel files
            if input_path.endswith('.csv'):
                df_raw = pd.read_csv(input_path)
            else:
                df_raw = pd.read_excel(input_path)
            
            log_processing_step(tracker_path, "Loaded raw input file", len(df_raw), input_path)
            df_01 = step_01_clean_and_standardize(df_raw, list_name, tracker_path)
            save_to_folder(df_01, step01_folder, list_name, tracker_path=tracker_path)

    df_02 = step_02_remove_phones(df_01, tracker_path)
    filepath_02 = save_to_folder(df_02, os.path.join(individual_output_folder, "2BSkip"), list_name, tracker_path=tracker_path)

    df_03 = step_03_dedupe_and_cleanup(df_01, list_name, individual_output_folder, tracker_path)
    filepath_03 = save_to_folder(df_03, os.path.join(individual_output_folder, "CC Ready"), list_name, tracker_path=tracker_path)
    
    # Process the Step03 (CC Ready) file to remove Type columns and swap Phone4/Phone5
    process_step03_file(filepath_03, tracker_path)
    remove_type_columns_from_cc_ready(filepath_03)

    df_04 = step_04_remove_landlines(df_03, tracker_path)
    filepath_04 = save_to_folder(df_04, os.path.join(individual_output_folder, "SC Ready"), list_name, tracker_path=tracker_path)

    df_05 = step_05_reshape(df_04, tracker_path)
    filepath_05 = save_to_folder(df_05, os.path.join(individual_output_folder, "GHL Ready"), list_name, tracker_path=tracker_path)

    # Create final record count tracker
    tracker_data = {
        "SkipTraced": len(df_01),
        "2BSkip": len(df_02),
        "CC Ready": len(df_03),
        "SC Ready": len(df_04),
        "GHL Ready": len(df_05)
    }
    
    # Create the list building records tracker
    tracker_lines = []
    for label, count in tracker_data.items():
        tracker_lines.append(f"{label}: {count}")
    
    list_tracker_path = os.path.join(individual_output_folder, "List Building Records.txt")
    with open(list_tracker_path, "w") as f:
        f.write(f"List Building Records - {list_name}\n")
        f.write("=" * 40 + "\n")
        f.write("\n".join(tracker_lines))
        f.write(f"\n\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # log_processing_step(tracker_path, "List Building Records Created", 0, list_tracker_path)
    
    # Finalize the tracking log
    finalize_tracking_log(tracker_path, 6, success=True)
    
    print("📋 Trackers saved:")
    # print(f"   - Processing tracker: {tracker_path}")
    print(f"   - List building records: {list_tracker_path}")
    
    return [filepath_01, filepath_02, filepath_03, filepath_04, filepath_05], tracker_data

# -------------------------
# Process directory for AAE 3 Phone LSB
# -------------------------
def process_aae_directory(input_folder, process_step01_files=False):
    output_folder = os.path.join(input_folder, "AAE_3_Phone_LSB_Output")
    ensure_folder(output_folder)
    
    all_trackers = {}
    
    # Process all files in the input folder
    for file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file)
        list_name = os.path.splitext(file)[0]
        
        # Check if we should process this file
        should_process = False
        is_step01_file = False
        
        if process_step01_files and file.endswith(".xlsx"):
            # Check if this is a Step01 file by looking for specific columns
            try:
                df_check = pd.read_excel(file_path, nrows=1)
                if all(col in df_check.columns for col in ['First Name', 'Last Name', 'Phone1', 'Type1']):
                    is_step01_file = True
                    should_process = True
            except:
                pass
        elif not process_step01_files and (file.endswith(".csv") or file.endswith(".xlsx")):
            should_process = True
        
        if should_process:
            print(f"\n{'='*50}")
            print(f"Processing {list_name}...")
            print(f"{'='*50}")
            
            # Create individual subfolders for this list
            individual_output_folder = os.path.join(output_folder, list_name)
            ensure_folder(individual_output_folder)
            
            # Create subfolders for this specific list
            subfolders = ["SkipTraced", "2BSkip", "CC Ready", "SC Ready", "GHL Ready", "No Hit"]
            for folder in subfolders:
                ensure_folder(os.path.join(individual_output_folder, folder))
            
            # Run the pipeline and capture tracker data
            _, tracker_data = run_aae_pipeline(file_path, list_name, output_folder, is_step01_file)
            all_trackers[list_name] = tracker_data
    
    # Create a summary tracker for all processed lists
    if all_trackers:
        create_summary_tracker(output_folder, all_trackers)
    
    print("\n✅ AAE 3 Phone LSB processing complete!")
    return all_trackers

# -------------------------
# Main execution
# -------------------------
if __name__ == "__main__":
    # Example usage:
    # process_aae_directory("path/to/your/input/folder")
    # or for individual file: run_aae_pipeline("path/to/file.csv", "ListName", "output/folder")
    
    print("AAE 3 Phone LSB Pipeline Script with Tracking Loaded")
    print("Available functions:")
    print("- process_aae_directory(input_folder, process_step01_files=False)")
    print("- run_aae_pipeline(input_path, list_name, output_folder, is_step01_file=False)")
    print("- process_step03_file(file_path)  # For individual CC Ready file processing")