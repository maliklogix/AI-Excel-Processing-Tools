
````
# AI-Excel-Processing-Tools ( Data Tools)

A powerful, GUI-based toolkit designed for high-volume CSV and Excel data processing. Tailored specifically for real estate investors, marketers, and data analysts, this tool helps automate complex list-building and data-cleaning workflows.

## 🚀 Key Features

- **Comprehensive Pipelines**: Automated workflows for handling Vacant Lot, Resident Data, and AAE lists.
  
- **Smart Data Manipulation**:
  - **Merge & Subtract**: Combine multiple datasets or remove overlaps using composite key matching.
  - **Smart Separator**: Split large files by unique column values (e.g., County, Zip).
  - **Column Mapper & Adder**: An interactive UI for aligning data to standard schemas and bulk-injecting new columns.

- **CRM Ready Outputs**: Automatically generate CSV files formatted for use with GoHighLevel (GHL) and other CRM platforms.

- **Record Collection**: Automatically gather processed files from nested directories into a central location.

- **Format Conversion**: Type-safe conversion between CSV and XLSX formats.

---

## 🛠️ Installation

### 1. Clone the repository:

```bash
git clone https://github.com/maliklogix/AI-Excel-Processing-Tools.git
cd AI-Excel-Processing-Tools
````

### 2. Install dependencies:

```bash
pip install pandas ttkbootstrap openpyxl xlsxwriter
```

### 3. Run the application:

```bash
python run.py
```

---

## 📂 Project Structure

* **run.py**: Application entry point.
* **main/**: Core application logic and dashboard definitions.
* **pipeline/**: Specialized workflows for real estate data.
* **utils/**: Modular tools for merging, converting, and cleaning data.
* **ui/**: GUI implementation and theme management.

---

## 📖 Usage

1. Launch the app by running `run.py`.
2. Choose a tool from the dashboard (e.g., **File Merger**, **Record Subtractor**, **Bulk List Builder**).
3. Follow the interactive prompts to select your input files/folders and output destinations.
4. Monitor progress through the built-in loading bars and status updates.

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

```

Now everything is encapsulated in one single code block. You can paste this directly into your GitHub README without losing any formatting! Let me know if there's anything else you'd like to modify.
```
