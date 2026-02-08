AI-Excel-Processing-Tools (Hitrotech Data Tools)

A powerful, GUI-based toolkit for high-volume CSV and Excel data processing. Designed specifically for real estate investors, marketers, and data analysts to automate complex list-building and data-cleaning workflows.

🚀 Key Features

•
Comprehensive Pipelines: Automated workflows for Vacant Lot, Resident Data, and AAE lists.

•
Smart Data Manipulation:

•
Merge & Subtract: Combine multiple datasets or remove overlaps with composite key matching.

•
Smart Separator: Split large files by unique column values (e.g., County, Zip).

•
Column Mapper & Adder: Interactive UI for aligning data to standard schemas and bulk-injecting columns.



•
CRM Ready Outputs: Generate "GHL Ready" CSVs formatted perfectly for GoHighLevel and other CRM platforms.

•
Record Collection: Automatically gather processed files from nested directories into one central location.

•
Format Conversion: Fast, type-safe conversion between CSV and XLSX.

🛠️ Installation

1.
Clone the repository:

Bash


git clone https://github.com/maliklogix/AI-Excel-Processing-Tools.git
cd AI-Excel-Processing-Tools





2.
Install dependencies:

Bash


pip install pandas ttkbootstrap openpyxl xlsxwriter





3.
Run the application:

Bash


python run.py





📂 Project Structure

•
run.py: Application entry point.

•
main/: Core application logic and dashboard definitions.

•
pipeline/: Specialized workflows for real estate data.

•
utils/: Modular tools for merging, converting, and cleaning.

•
ui/: GUI implementation and theme management.

📖 Usage

1.
Launch the app via run.py.

2.
Choose a tool from the dashboard (e.g., File Merger, Record Subtractor, or Bulk List Builder ).

3.
Follow the interactive prompts to select your input files/folders and output destinations.

4.
Monitor progress via the built-in loading bars and status updates.

🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

📄 License

This project is licensed under the MIT License.

