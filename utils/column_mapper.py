import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import re
from .helpers import ensure_folder, save_excel

# Standard schema - now editable
# Updated REQUIRED_COLUMNS with phone types and email
REQUIRED_COLUMNS = [
    "First Name", "Last Name", "Property Address", "Property City", "Property State", "Property Zip",
    "Mailing Address", "Mailing City", "Mailing State", "Mailing Zip",
    "Phone1", "Type1", "Phone2", "Type2", "Phone3", "Type3", 
    "Phone4", "Type4", "Phone5", "Type5", "Phone6", "Type6", 
    "Email", "List"
]

# Expanded auto-map dictionary with variations for all required columns including phone types and email
AUTO_MAP_DICT = {
    # First Name variations (10)
    'first_name': 'First Name',
    'first name': 'First Name',
    'firstname': 'First Name',
    'fname': 'First Name',
    'f_name': 'First Name',
    'given_name': 'First Name',
    'given name': 'First Name',
    'givenname': 'First Name',
    'first': 'First Name',
    'fn': 'First Name',
    
    # Last Name variations (10)
    'last_name': 'Last Name',
    'last name': 'Last Name',
    'lastname': 'Last Name',
    'lname': 'Last Name',
    'l_name': 'Last Name',
    'surname': 'Last Name',
    'family_name': 'Last Name',
    'family name': 'Last Name',
    'last': 'Last Name',
    'ln': 'Last Name',
    
    # Property Address variations (10)
    'associated_property_address_line_1': 'Property Address',
    'property_address': 'Property Address',
    'property address': 'Property Address',
    'propertyaddress': 'Property Address',
    'prop_address': 'Property Address',
    'prop address': 'Property Address',
    'property_street': 'Property Address',
    'property street': 'Property Address',
    'prop_street': 'Property Address',
    'address': 'Property Address',
    
    # Property City variations (10)
    'associated_property_address_city': 'Property City',
    'property_city': 'Property City',
    'property city': 'Property City',
    'propertycity': 'Property City',
    'prop_city': 'Property City',
    'prop city': 'Property City',
    'city': 'Property City',
    'property_town': 'Property City',
    'property town': 'Property City',
    'prop_town': 'Property City',
    
    # Property State variations (10)
    'associated_property_address_state': 'Property State',
    'property_state': 'Property State',
    'property state': 'Property State',
    'propertystate': 'Property State',
    'prop_state': 'Property State',
    'prop state': 'Property State',
    'state': 'Property State',
    'property_province': 'Property State',
    'property province': 'Property State',
    'prop_province': 'Property State',
    
    # Property Zip variations (10)
    'associated_property_address_zipcode': 'Property Zip',
    'property_zip': 'Property Zip',
    'property zip': 'Property Zip',
    'propertyzip': 'Property Zip',
    'prop_zip': 'Property Zip',
    'prop zip': 'Property Zip',
    'zip': 'Property Zip',
    'property_zipcode': 'Property Zip',
    'property zipcode': 'Property Zip',
    'zipcode': 'Property Zip',
    
    # Mailing Address variations (10)
    'primary_mailing_address': 'Mailing Address',
    'mailing_address': 'Mailing Address',
    'mailing address': 'Mailing Address',
    'mailingaddress': 'Mailing Address',
    'mail_address': 'Mailing Address',
    'mail address': 'Mailing Address',
    'mailing_street': 'Mailing Address',
    'mailing street': 'Mailing Address',
    'mail_street': 'Mailing Address',
    'mailing_addr': 'Mailing Address',
    
    # Mailing City variations (10)
    'primary_mailing_city': 'Mailing City',
    'mailing_city': 'Mailing City',
    'mailing city': 'Mailing City',
    'mailingcity': 'Mailing City',
    'mail_city': 'Mailing City',
    'mail city': 'Mailing City',
    'mailing_town': 'Mailing City',
    'mailing town': 'Mailing City',
    'mail_town': 'Mailing City',
    'mailing_city_name': 'Mailing City',
    
    # Mailing State variations (10)
    'primary_mailing_state': 'Mailing State',
    'mailing_state': 'Mailing State',
    'mailing state': 'Mailing State',
    'mailingstate': 'Mailing State',
    'mail_state': 'Mailing State',
    'mail state': 'Mailing State',
    'mailing_province': 'Mailing State',
    'mailing province': 'Mailing State',
    'mail_province': 'Mailing State',
    'mailing_state_name': 'Mailing State',
    
    # Mailing Zip variations (10)
    'primary_mailing_zip': 'Mailing Zip',
    'mailing_zip': 'Mailing Zip',
    'mailing zip': 'Mailing Zip',
    'mailingzip': 'Mailing Zip',
    'mail_zip': 'Mailing Zip',
    'mail zip': 'Mailing Zip',
    'mailing_zipcode': 'Mailing Zip',
    'mailing zipcode': 'Mailing Zip',
    'mail_zipcode': 'Mailing Zip',
    'mailing_postal': 'Mailing Zip',
    
    # Phone1 variations (10)
    'phone_1': 'Phone1',
    'phone1': 'Phone1',
    'phone 1': 'Phone1',
    'primary_phone': 'Phone1',
    'primary phone': 'Phone1',
    'primaryphone': 'Phone1',
    'main_phone': 'Phone1',
    'main phone': 'Phone1',
    'mainphone': 'Phone1',
    'phone_primary': 'Phone1',
    
    # Type1 variations (10)
    'phone_1_type': 'Type1',
    'phone1_type': 'Type1',
    'phone 1 type': 'Type1',
    'phone_type_1': 'Type1',
    'phonetype1': 'Type1',
    'phone_type1': 'Type1',
    'type_phone_1': 'Type1',
    'type_phone1': 'Type1',
    'phone1type': 'Type1',
    'type1': 'Type1',
    
    # Phone2 variations (10)
    'phone_2': 'Phone2',
    'phone2': 'Phone2',
    'phone 2': 'Phone2',
    'secondary_phone': 'Phone2',
    'secondary phone': 'Phone2',
    'secondaryphone': 'Phone2',
    'alt_phone': 'Phone2',
    'alt phone': 'Phone2',
    'altphone': 'Phone2',
    'phone_secondary': 'Phone2',
    
    # Type2 variations (10)
    'phone_2_type': 'Type2',
    'phone2_type': 'Type2',
    'phone 2 type': 'Type2',
    'phone_type_2': 'Type2',
    'phonetype2': 'Type2',
    'phone_type2': 'Type2',
    'type_phone_2': 'Type2',
    'type_phone2': 'Type2',
    'phone2type': 'Type2',
    'type2': 'Type2',
    
    # Phone3 variations (10)
    'phone_3': 'Phone3',
    'phone3': 'Phone3',
    'phone 3': 'Phone3',
    'tertiary_phone': 'Phone3',
    'tertiary phone': 'Phone3',
    'tertiaryphone': 'Phone3',
    'other_phone': 'Phone3',
    'other phone': 'Phone3',
    'otherphone': 'Phone3',
    'phone_other': 'Phone3',
    
    # Type3 variations (10)
    'phone_3_type': 'Type3',
    'phone3_type': 'Type3',
    'phone 3 type': 'Type3',
    'phone_type_3': 'Type3',
    'phonetype3': 'Type3',
    'phone_type3': 'Type3',
    'type_phone_3': 'Type3',
    'type_phone3': 'Type3',
    'phone3type': 'Type3',
    'type3': 'Type3',
    
    # Phone4 variations (10)
    'phone_4': 'Phone4',
    'phone4': 'Phone4',
    'phone 4': 'Phone4',
    'phone_four': 'Phone4',
    'phone four': 'Phone4',
    'phonefour': 'Phone4',
    'additional_phone': 'Phone4',
    'additional phone': 'Phone4',
    'additionalphone': 'Phone4',
    'phone_additional': 'Phone4',
    
    # Type4 variations (10)
    'phone_4_type': 'Type4',
    'phone4_type': 'Type4',
    'phone 4 type': 'Type4',
    'phone_type_4': 'Type4',
    'phonetype4': 'Type4',
    'phone_type4': 'Type4',
    'type_phone_4': 'Type4',
    'type_phone4': 'Type4',
    'phone4type': 'Type4',
    'type4': 'Type4',
    
    # Phone5 variations (10)
    'phone_5': 'Phone5',
    'phone5': 'Phone5',
    'phone 5': 'Phone5',
    'phone_five': 'Phone5',
    'phone five': 'Phone5',
    'phonefive': 'Phone5',
    'extra_phone': 'Phone5',
    'extra phone': 'Phone5',
    'extraphone': 'Phone5',
    'phone_extra': 'Phone5',
    
    # Type5 variations (10)
    'phone_5_type': 'Type5',
    'phone5_type': 'Type5',
    'phone 5 type': 'Type5',
    'phone_type_5': 'Type5',
    'phonetype5': 'Type5',
    'phone_type5': 'Type5',
    'type_phone_5': 'Type5',
    'type_phone5': 'Type5',
    'phone5type': 'Type5',
    'type5': 'Type5',
    
    # Phone6 variations (10)
    'phone_6': 'Phone6',
    'phone6': 'Phone6',
    'phone 6': 'Phone6',
    'phone_six': 'Phone6',
    'phone six': 'Phone6',
    'phonesix': 'Phone6',
    'backup_phone': 'Phone6',
    'backup phone': 'Phone6',
    'backupphone': 'Phone6',
    'phone_backup': 'Phone6',
    
    # Type6 variations (10)
    'phone_6_type': 'Type6',
    'phone6_type': 'Type6',
    'phone 6 type': 'Type6',
    'phone_type_6': 'Type6',
    'phonetype6': 'Type6',
    'phone_type6': 'Type6',
    'type_phone_6': 'Type6',
    'type_phone6': 'Type6',
    'phone6type': 'Type6',
    'type6': 'Type6',
    
    # Email variations (10)
    'email': 'Email',
    'email_address': 'Email',
    'email address': 'Email',
    'emailaddress': 'Email',
    'e_mail': 'Email',
    'e mail': 'Email',
    'email_addr': 'Email',
    'email addr': 'Email',
    'contact_email': 'Email',
    'contact email': 'Email',
    
    # List variations (10)
    'list': 'List',
    'list_name': 'List',
    'list name': 'List',
    'listname': 'List',
    'campaign': 'List',
    'campaign_name': 'List',
    'campaign name': 'List',
    'campaignname': 'List',
    'source': 'List',
    'source_name': 'List',
}


# Additional optional columns that can be added
OPTIONAL_COLUMNS = [
    "Email", "Owner Occupied", "Property Type", "Bedrooms", "Bathrooms",
    "Square Footage", "Lot Size", "Year Built", "Property Value", "Last Sale Date",
    "Last Sale Price", "Estimated Equity", "LTV", "Mortgage Balance", "Tax Value"
]

# Data transformation functions
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

def split_owner_name(df):
    """Split Owner Name column into First Name and Last Name if exists"""
    if "Owner Name" in df.columns:
        df["Owner Name"] = df["Owner Name"].astype(str).str.strip()
        df["First Name"] = df["Owner Name"].apply(lambda x: x.split(" ", 1)[0] if x else "")
        df["Last Name"] = df["Owner Name"].apply(lambda x: x.split(" ", 1)[1] if " " in x else "")
    return df

# Transformation options for columns
TRANSFORMATION_OPTIONS = {
    "None": lambda x: x,
    "Pascal Case": to_pascal_case,
    "Normalize Address": normalize_address,
    "Trim Whitespace": lambda x: x.strip() if isinstance(x, str) else x,
    "Uppercase": lambda x: x.upper() if isinstance(x, str) else x,
    "Lowercase": lambda x: x.lower() if isinstance(x, str) else x,
    "Capitalize Words": lambda x: x.title() if isinstance(x, str) else x,
    "Extract Email": lambda df: extract_email_column(df)[1],
}

# Predefined operations that can be applied
PREDEFINED_OPERATIONS = {
    "Split Owner Name": split_owner_name,
    "Standardize Mailing Address": lambda df: df.apply(
        lambda col: col.apply(to_pascal_case) if col.name in ['Mailing Address', 'Mailing City'] else col
    ),
}


def run_column_mapper(file, project_root=None):
    try:
        df = pd.read_csv(file) if file.endswith(".csv") else pd.read_excel(file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")
        return
    
    win = tk.Toplevel()
    win.title("Advanced Column Mapper Tool")
    win.geometry("1000x800")
    
    # Create notebook for tabs
    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Main mapping frame
    mapping_frame = ttk.Frame(notebook, padding=10)
    notebook.add(mapping_frame, text="Column Mapping")
    
    # Settings frame
    settings_frame = ttk.Frame(notebook, padding=10)
    notebook.add(settings_frame, text="Settings")
    
    # Preview frame
    preview_frame = ttk.Frame(notebook, padding=10)
    notebook.add(preview_frame, text="Data Preview")
    
    # Operations frame
    operations_frame = ttk.Frame(notebook, padding=10)
    notebook.add(operations_frame, text="Operations")
    
    mapping_frames = []
    custom_list_value = tk.StringVar()
    
    # Create a scrollable frame for mappings
    canvas = tk.Canvas(mapping_frame)
    scrollbar = ttk.Scrollbar(mapping_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # --- Function: remove a mapping row ---
    def remove_row(frame):
        frame.destroy()
        for item in mapping_frames:
            if item["frame"] == frame:
                mapping_frames.remove(item)
                break
    
    # --- Function: add a new mapping row ---
    def add_custom_column():
        def save_new_column():
            new_col = new_col_var.get().strip()
            if new_col:
                build_row(new_col, is_custom=True)
                add_win.destroy()
        
        add_win = tk.Toplevel(win)
        add_win.title("Add Custom Column")
        
        tk.Label(add_win, text="Column Name:").pack(pady=5)
        new_col_var = tk.StringVar()
        tk.Entry(add_win, textvariable=new_col_var, width=30).pack(pady=5)
        tk.Button(add_win, text="Add", command=save_new_column).pack(pady=5)
    
    # --- Function: build one row ---
    def build_row(req, is_custom=False):
        frame = tk.Frame(scrollable_frame, pady=2)
        frame.pack(fill="x", padx=5)
        
        enabled = tk.BooleanVar(value=True)
        
        tk.Checkbutton(frame, variable=enabled).pack(side="left")
        
        # Different background for custom columns
        bg_color = "white" if not is_custom else "#f0f0ff"
        
        # Column name with edit capability
        col_name_var = tk.StringVar(value=req)
        col_entry = tk.Entry(frame, textvariable=col_name_var, width=18, bg=bg_color)
        col_entry.pack(side="left")
        
        combo = ttk.Combobox(frame, values=list(df.columns), width=25)
        combo.pack(side="left", padx=5)
        
        # Transformation dropdown
        transform_var = tk.StringVar(value="None")
        transform_combo = ttk.Combobox(frame, textvariable=transform_var, 
                                     values=list(TRANSFORMATION_OPTIONS.keys()), width=15)
        transform_combo.pack(side="left", padx=5)
        
        # Auto-map if found
        for col in df.columns:
            if col.lower() in AUTO_MAP_DICT and AUTO_MAP_DICT[col.lower()] == req:
                combo.set(col)
                break
        
        # Special case: List can also have custom text
        entry = None
        if req == "List":
            entry = tk.Entry(frame, textvariable=custom_list_value, width=15)
            entry.pack(side="left", padx=5)
        
        # Delete button only for custom columns
        if is_custom:
            btn = tk.Button(frame, text="❌", command=lambda f=frame: remove_row(f), fg="red")
            btn.pack(side="left", padx=5)
        
        mapping_frames.append({
            "frame": frame,
            "req": req,
            "enabled": enabled,
            "combo": combo,
            "entry": entry,
            "is_custom": is_custom,
            "name_var": col_name_var,
            "transform_var": transform_var
        })
    
    # Build rows for required columns
    for req in REQUIRED_COLUMNS:
        build_row(req)
    
    # Add button for custom columns
    add_btn_frame = tk.Frame(scrollable_frame)
    add_btn_frame.pack(fill="x", pady=10)
    tk.Button(add_btn_frame, text="+ Add Custom Column", command=add_custom_column).pack()
    
    # --- Settings Tab Content ---
    def save_settings():
        # Update REQUIRED_COLUMNS and AUTO_MAP_DICT based on settings
        new_required = req_cols_text.get("1.0", tk.END).strip().split('\n')
        new_auto_map = {}
        
        for line in auto_map_text.get("1.0", tk.END).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                new_auto_map[key.strip()] = value.strip()
        
        # Update global variables
        globals()['REQUIRED_COLUMNS'] = new_required
        globals()['AUTO_MAP_DICT'] = new_auto_map
        
        messagebox.showinfo("Settings", "Settings saved. Restart the mapper to see changes.")
    
    # Settings for required columns
    tk.Label(settings_frame, text="Required Columns (one per line):").grid(row=0, column=0, sticky="w", pady=5)
    req_cols_text = scrolledtext.ScrolledText(settings_frame, width=30, height=15)
    req_cols_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
    
    # Insert current required columns
    req_cols_text.insert("1.0", "\n".join(REQUIRED_COLUMNS))
    
    # Settings for auto-mapping
    tk.Label(settings_frame, text="Auto-Map Dictionary (key:value, one per line):").grid(row=0, column=1, sticky="w", pady=5)
    auto_map_text = scrolledtext.ScrolledText(settings_frame, width=30, height=15)
    auto_map_text.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
    
    # Insert current auto-map dictionary
    auto_map_content = "\n".join([f"{k}:{v}" for k, v in AUTO_MAP_DICT.items()])
    auto_map_text.insert("1.0", auto_map_content)
    
    # Save settings button
    tk.Button(settings_frame, text="Save Settings", command=save_settings).grid(row=2, column=0, columnspan=2, pady=10)
    
    # --- Preview Tab Content ---
    # Show a preview of the data
    preview_text = scrolledtext.ScrolledText(preview_frame, width=100, height=20)
    preview_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Display first few rows and column info
    preview_info = f"File: {os.path.basename(file)}\n"
    preview_info += f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n\n"
    preview_info += "Columns:\n" + ", ".join(df.columns.tolist()) + "\n\n"
    preview_info += "First 5 rows:\n" + str(df.head())
    
    preview_text.insert("1.0", preview_info)
    preview_text.config(state="disabled")
    
    # --- Operations Tab Content ---
    operations_var = tk.StringVar(value="None")
    
    tk.Label(operations_frame, text="Select Predefined Operations:").pack(pady=5)
    
    for op_name in PREDEFINED_OPERATIONS.keys():
        rb = ttk.Radiobutton(operations_frame, text=op_name, value=op_name, variable=operations_var)
        rb.pack(anchor="w", padx=20)
    
    # --- Apply Mapping ---
        # --- Apply Mapping ---
    def apply_mapping():
        new_df = pd.DataFrame()
        operations_to_apply = []

        # Collect operations if any selected
        if operations_var.get() != "None":
            operations_to_apply.append(PREDEFINED_OPERATIONS[operations_var.get()])

        for item in mapping_frames:
            req = item["name_var"].get()  # Use the editable column name
            if not item["enabled"].get():  # unchecked → skip
                continue

            if req == "List":
                custom_val = custom_list_value.get().strip()
                selected = item["combo"].get()

                if custom_val:
                    new_df[req] = [custom_val] * len(df)
                elif selected and selected in df.columns:
                    new_df[req] = df[selected]
            else:
                selected = item["combo"].get()
                transform = item["transform_var"].get()
                
                if selected and selected in df.columns:
                    # Apply transformation if selected
                    if transform != "None":
                        if transform == "Extract Email":
                            _, email_data = extract_email_column(df)
                            new_df[req] = email_data
                        else:
                            new_df[req] = df[selected].apply(TRANSFORMATION_OPTIONS[transform])
                    else:
                        new_df[req] = df[selected]

        # ✅ Extra step: Auto transformations (Pascal + Zip cleaning)
        if "First Name" in new_df.columns:
            new_df["First Name"] = new_df["First Name"].apply(to_pascal_case)
        if "Last Name" in new_df.columns:
            new_df["Last Name"] = new_df["Last Name"].apply(to_pascal_case)
        if "Property Address" in new_df.columns:
            new_df["Property Address"] = new_df["Property Address"].apply(to_pascal_case)
        if "Property City" in new_df.columns:
            new_df["Property City"] = new_df["Property City"].apply(to_pascal_case)
        if "Mailing Address" in new_df.columns:
            new_df["Mailing Address"] = new_df["Mailing Address"].apply(to_pascal_case)
        if "Mailing State" in new_df.columns:
            new_df["Mailing State"] = new_df["Mailing State"].apply(to_pascal_case)

        # ✅ Clean Zips (remove after "-")
        for zip_col in ["Property Zip", "Mailing Zip"]:
            if zip_col in new_df.columns:
                new_df[zip_col] = new_df[zip_col].astype(str).str.split("-").str[0].str.strip()

        # Check if we have any data
        if new_df.empty:
            messagebox.showwarning("Warning", "No columns were mapped. Please select at least one column to map.")
            return

        # Apply predefined operations
        for operation in operations_to_apply:
            new_df = operation(new_df)

        # Save in the same directory as the input file
        input_dir = os.path.dirname(file)
        base_name = os.path.splitext(os.path.basename(file))[0]
        output_file = os.path.join(input_dir, f"{base_name}_mapped.xlsx")

        try:
            save_excel(new_df, output_file)
            messagebox.showinfo("✅ Done", f"Mapped file saved:\n{output_file}")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")


    # Add apply button at the bottom
    button_frame = tk.Frame(win)
    button_frame.pack(fill="x", pady=10)
    
    tk.Button(button_frame, text="Apply Mapping & Save", command=apply_mapping, bg="#4CAF50", fg="white", 
              font=("Arial", 10, "bold")).pack(side="right", padx=10)
    
    # Add a button to add optional columns
    def add_optional_columns():
        def add_selected():
            selected = [OPTIONAL_COLUMNS[i] for i in lb.curselection()]
            for col in selected:
                build_row(col, is_custom=True)
            opt_win.destroy()
        
        opt_win = tk.Toplevel(win)
        opt_win.title("Add Optional Columns")
        opt_win.geometry("300x400")
        
        tk.Label(opt_win, text="Select columns to add:").pack(pady=5)
        
        lb = tk.Listbox(opt_win, selectmode=tk.MULTIPLE)
        for col in OPTIONAL_COLUMNS:
            lb.insert(tk.END, col)
        lb.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Button(opt_win, text="Add Selected", command=add_selected).pack(pady=10)
    
    tk.Button(button_frame, text="Add Optional Columns", command=add_optional_columns).pack(side="left", padx=10)

    win.mainloop()