import os
import shutil
import tkinter as tk
from tkinter import messagebox

def run_record_collector(base_directory, folder_name):
    """
    Collect all files from folders with the specified name recursively
    and copy them to a main folder in the base directory.
    
    Args:
        base_directory: The root directory to search in
        folder_name: The name of the folder to search for
    """
    target_folder = os.path.join(base_directory, folder_name)
    
    # Make target folder if it doesn't exist
    os.makedirs(target_folder, exist_ok=True)
    
    files_copied = 0
    
    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(base_directory):
        # If folder name matches and it's not the target folder itself
        if os.path.basename(root) == folder_name and root != target_folder:
            for file in files:
                source_file = os.path.join(root, file)
                dest_file = os.path.join(target_folder, file)
                
                # If file with same name exists, rename with suffix
                if os.path.exists(dest_file):
                    base, ext = os.path.splitext(file)
                    i = 1
                    while os.path.exists(os.path.join(target_folder, f"{base}_{i}{ext}")):
                        i += 1
                    dest_file = os.path.join(target_folder, f"{base}_{i}{ext}")
                
                try:
                    shutil.copy2(source_file, dest_file)
                    files_copied += 1
                    print(f"✅ Copied: {source_file} -> {dest_file}")
                except Exception as e:
                    print(f"❌ Error copying {source_file}: {e}")
    
    print(f"\n🎯 {files_copied} files collected into: {target_folder}")
    
    # Show completion message
    if files_copied > 0:
        messagebox.showinfo("Record Collector", 
                           f"Successfully collected {files_copied} files into:\n{target_folder}")
    else:
        messagebox.showwarning("Record Collector", 
                              f"No files found in '{folder_name}' folders within:\n{base_directory}")

if __name__ == "__main__":
    # For testing directly
    base_dir = input("Enter base directory: ").strip()
    folder_to_collect = input("Enter folder name to collect: ").strip()
    
    if not base_dir or not folder_to_collect:
        print("Please provide both base directory and folder name")
    else:
        run_record_collector(base_dir, folder_to_collect)