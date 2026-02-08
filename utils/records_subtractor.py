import os
import pandas as pd
import argparse
import sys
from pathlib import Path

def subtract_records(left_files, right_files, left_columns, right_columns, output_path, output_format="xlsx"):
    """
    Subtract records from right files from left files and save the result
    
    Args:
        left_files (list): List of paths to left side files (records to keep)
        right_files (list): List of paths to right side files (records to subtract)
        left_columns (list): List of column names to combine for left side
        right_columns (list): List of column names to combine for right side
        output_path (str): Path to save the output file
        output_format (str): Output format - 'xlsx' or 'csv'
    """
    
    print("🔍 Reading left side files...")
    
    # Read and combine left side files
    left_dfs = []
    for i, file in enumerate(left_files):
        print(f"   Reading left file {i+1}/{len(left_files)}: {os.path.basename(file)}")
        
        if file.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        left_dfs.append(df)
    
    print("📊 Combining left side data...")
    left_combined = pd.concat(left_dfs, ignore_index=True)
    
    # Create composite key for left side
    left_combined['composite_key'] = left_combined[left_columns].astype(str).agg('_'.join, axis=1)
    
    print("🔍 Reading right side files...")
    
    # Read and combine right side files
    right_dfs = []
    for i, file in enumerate(right_files):
        print(f"   Reading right file {i+1}/{len(right_files)}: {os.path.basename(file)}")
        
        if file.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        right_dfs.append(df)
    
    print("📊 Combining right side data...")
    right_combined = pd.concat(right_dfs, ignore_index=True)
    
    # Create composite key for right side
    right_combined['composite_key'] = right_combined[right_columns].astype(str).agg('_'.join, axis=1)
    
    print("➖ Performing subtraction...")
    
    # Find records in left that are not in right
    right_keys = set(right_combined['composite_key'].values)
    left_combined = left_combined[~left_combined['composite_key'].isin(right_keys)]
    
    # Remove the composite key column
    left_combined = left_combined.drop(columns=['composite_key'])
    
    print("💾 Saving result...")
    
    # Save the result
    if output_format == "csv":
        left_combined.to_csv(output_path, index=False)
    else:
        left_combined.to_excel(output_path, index=False)
    
    print(f"✅ Subtraction completed! Result saved to: {output_path}")
    print(f"📊 Original records: {len(left_dfs[0]) + sum(len(df) for df in left_dfs[1:])}")
    print(f"📊 Records after subtraction: {len(left_combined)}")
    print(f"📊 Records removed: {len(left_dfs[0]) + sum(len(df) for df in left_dfs[1:]) - len(left_combined)}")

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="Subtract records from one set of files from another")
    
    parser.add_argument("--left", "-l", nargs="+", required=True, 
                       help="Left side files (records to keep)")
    parser.add_argument("--right", "-r", nargs="+", required=True,
                       help="Right side files (records to subtract)")
    parser.add_argument("--left-cols", "-lc", required=True,
                       help="Left side columns to combine (comma-separated)")
    parser.add_argument("--right-cols", "-rc", required=True,
                       help="Right side columns to combine (comma-separated)")
    parser.add_argument("--output", "-o", required=True,
                       help="Output file path")
    parser.add_argument("--format", "-f", choices=["xlsx", "csv"], default="xlsx",
                       help="Output format (default: xlsx)")
    
    args = parser.parse_args()
    
    # Check if files exist
    for file in args.left + args.right:
        if not os.path.exists(file):
            print(f"❌ Error: File not found: {file}")
            sys.exit(1)
    
    # Parse column lists
    left_columns = [col.strip() for col in args.left_cols.split(",") if col.strip()]
    right_columns = [col.strip() for col in args.right_cols.split(",") if col.strip()]
    
    if not left_columns:
        print("❌ Error: No valid columns specified for left side")
        sys.exit(1)
        
    if not right_columns:
        print("❌ Error: No valid columns specified for right side")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        subtract_records(
            left_files=args.left,
            right_files=args.right,
            left_columns=left_columns,
            right_columns=right_columns,
            output_path=args.output,
            output_format=args.format
        )
    except Exception as e:
        print(f"❌ Error during subtraction: {str(e)}")
        sys.exit(1)

def subtract_folders(left_folder, right_folder, left_columns, right_columns, output_folder, file_pattern="*.xlsx", output_format="xlsx"):
    """
    Subtract records from all files in right folder from files in left folder
    
    Args:
        left_folder (str): Path to folder with left side files
        right_folder (str): Path to folder with right side files
        left_columns (list): List of column names to combine for left side
        right_columns (list): List of column names to combine for right side
        output_folder (str): Path to save output files
        file_pattern (str): File pattern to match (e.g., "*.xlsx", "*.csv")
        output_format (str): Output format - 'xlsx' or 'csv'
    """
    
    if not os.path.exists(left_folder):
        raise ValueError(f"Left folder does not exist: {left_folder}")
    
    if not os.path.exists(right_folder):
        raise ValueError(f"Right folder does not exist: {right_folder}")
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all files matching pattern in left folder
    left_files = []
    for pattern in file_pattern.split(","):
        left_files.extend(Path(left_folder).glob(pattern.strip()))
    
    # Get all files matching pattern in right folder
    right_files = []
    for pattern in file_pattern.split(","):
        right_files.extend(Path(right_folder).glob(pattern.strip()))
    
    if not left_files:
        print(f"❌ No files found in left folder: {left_folder} with pattern: {file_pattern}")
        return
    
    if not right_files:
        print(f"❌ No files found in right folder: {right_folder} with pattern: {file_pattern}")
        return
    
    print(f"📁 Found {len(left_files)} files in left folder")
    print(f"📁 Found {len(right_files)} files in right folder")
    
    # Process each left file
    for left_file in left_files:
        try:
            print(f"\n🔍 Processing: {left_file.name}")
            
            # Read left file
            if left_file.suffix == '.csv':
                left_df = pd.read_csv(left_file)
            else:
                left_df = pd.read_excel(left_file)
            
            # Create composite key for left side
            left_df['composite_key'] = left_df[left_columns].astype(str).agg('_'.join, axis=1)
            
            # Read and combine all right files
            right_dfs = []
            for right_file in right_files:
                if right_file.suffix == '.csv':
                    right_df = pd.read_csv(right_file)
                else:
                    right_df = pd.read_excel(right_file)
                right_dfs.append(right_df)
            
            right_combined = pd.concat(right_dfs, ignore_index=True)
            
            # Create composite key for right side
            right_combined['composite_key'] = right_combined[right_columns].astype(str).agg('_'.join, axis=1)
            
            # Find records in left that are not in right
            right_keys = set(right_combined['composite_key'].values)
            result_df = left_df[~left_df['composite_key'].isin(right_keys)]
            
            # Remove the composite key column
            result_df = result_df.drop(columns=['composite_key'])
            
            # Save the result
            output_file = Path(output_folder) / f"subtracted_{left_file.name}"
            if output_format == "csv":
                output_file = output_file.with_suffix('.csv')
                result_df.to_csv(output_file, index=False)
            else:
                output_file = output_file.with_suffix('.xlsx')
                result_df.to_excel(output_file, index=False)
            
            print(f"✅ Saved: {output_file.name}")
            print(f"   Original: {len(left_df)} records, After subtraction: {len(result_df)} records")
            
        except Exception as e:
            print(f"❌ Error processing {left_file.name}: {str(e)}")

if __name__ == "__main__":
    main()