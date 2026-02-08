import os
import shutil
import tkinter as tk
from tkinter import messagebox

def collect_files_from_folders(base_path, target_folder_name):
    """
    Recursively search for folders with the specified name and collect all files from them.
    
    Args:
        base_path (str): The root directory to start searching from
        target_folder_name (str): The name of the folder to search for and collect files from
        
    Returns:
        tuple: (success_count, total_files_copied, target_folder_path)
    """
    target_folder = os.path.join(base_path, target_folder_name)
    
    # Make target folder if not exists
    os.makedirs(target_folder, exist_ok=True)
    
    success_count = 0
    total_files_copied = 0
    
    for root, dirs, files in os.walk(base_path):
        # If folder name matches our target (case insensitive)
        if os.path.basename(root).lower() == target_folder_name.lower():
            for file in files:
                source_file = os.path.join(root, file)
                dest_file = os.path.join(target_folder, file)
                
                # If duplicate file name exists, rename by adding suffix
                if os.path.exists(dest_file):
                    base, ext = os.path.splitext(file)
                    i = 1
                    while os.path.exists(os.path.join(target_folder, f"{base}_{i}{ext}")):
                        i += 1
                    dest_file = os.path.join(target_folder, f"{base}_{i}{ext}")
                
                try:
                    shutil.copy2(source_file, dest_file)
                    total_files_copied += 1
                except Exception as e:
                    print(f"❌ Failed to copy {source_file}: {e}")
                    continue
            
            success_count += 1
    
    return success_count, total_files_copied, target_folder

def run_files_collector_ui(parent, base_path, folder_name):
    """
    Run the file collection process and show results in a UI
    
    Args:
        parent: The parent window
        base_path (str): The base directory to search
        folder_name (str): The folder name to search for
    """
    if not base_path or not os.path.isdir(base_path):
        messagebox.showerror("Error", "Please select a valid base directory")
        return
        
    if not folder_name:
        messagebox.showerror("Error", "Please specify a folder name to search for")
        return
    
    # Create a progress window
    progress_win = tk.Toplevel(parent)
    progress_win.title("Collecting Files")
    progress_win.geometry("400x150")
    progress_win.transient(parent)
    progress_win.grab_set()
    
    tk.Label(progress_win, text=f"Searching for '{folder_name}' folders...", 
             font=("Arial", 12)).pack(pady=20)
    
    progress_var = tk.StringVar(value="Processing...")
    tk.Label(progress_win, textvariable=progress_var).pack(pady=10)
    
    progress_win.update()
    
    try:
        # Run the collection process
        folders_found, files_copied, target_path = collect_files_from_folders(base_path, folder_name)
        
        progress_win.destroy()
        
        if folders_found == 0:
            messagebox.showinfo("Complete", 
                               f"No folders named '{folder_name}' were found in:\n{base_path}")
        else:
            messagebox.showinfo("Complete", 
                               f"✅ Collected {files_copied} files from {folders_found} '{folder_name}' folders\n\n"
                               f"All files have been copied to:\n{target_path}")
    except Exception as e:
        progress_win.destroy()
        messagebox.showerror("Error", f"An error occurred during file collection:\n{str(e)}")