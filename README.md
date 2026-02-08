# AI-Excel-Processing-Tools (Data Tools)

## 📌 Overview

**AI-Excel-Processing-Tools** (internally known as **Hitrotech Data Tools**) is a powerful Python-based desktop application built for high-volume CSV and Excel data processing. It is specifically designed for real estate lead generation, marketing automation, and large-scale data workflows.

The application provides a centralized GUI dashboard built with **ttkbootstrap**, allowing users to automate complex list-building processes such as:

- Standardizing raw datasets  
- Removing duplicate records  
- Enriching records with multiple phone numbers  
- Preparing CRM-ready datasets for platforms like **GoHighLevel (GHL)**  

The project follows a modular and extensible architecture. The core system evolved from **main.py** to **main02.py** and **main03.py**, enabling continuous feature expansion while maintaining scalability and performance.

---

## 🚀 Key Features

### 🔹 Advanced Data Pipelines

The application provides multiple specialized automated pipelines tailored for different real estate data types:

- **Bulk List Builder**  
  Processes MCHB MPV and 6-phone vacant lot datasets through a full automation pipeline.

- **AAE List Builder**  
  Designed specifically for AAE lists with automated 3-phone enrichment and Step01 toggle functionality.

- **Resident Data Pipeline**  
  Handles resident-focused datasets with support for up to 6 phone numbers.

- **Vacant Lot Pipeline**  
  Builds detailed vacant lot datasets including property and mailing information.

---

### 🔹 Core Utility Tools

- **Smart Separator**  
  Splits large datasets into smaller files based on unique column values such as County or ZIP code.

- **Advanced File Merger**  
  Combines multiple CSV/XLSX files into a unified workbook with aligned columns and record summaries.

- **Record Subtractor**  
  Removes duplicate or overlapping records by comparing datasets using composite keys.

- **Column Mapper & Adder**  
  Interactive interface for mapping columns to standardized schemas and injecting new data from master files recursively.

- **Record Collector**  
  Automatically scans nested directories to collect targeted folders like *GHL Ready* or *SkipTraced* into a centralized location.

---

### 🔹 Format Conversion & Standardization

- **Bi-directional File Conversion**  
  Convert CSV ↔ XLSX while preserving data integrity, ZIP codes, and phone numbers.

- **GHL Compiler**  
  Transforms datasets into GoHighLevel-ready formats by expanding multiple phone numbers into separate rows.

- **Data Standardization Engine**  
  - Pascal case formatting for addresses and cities  
  - Phone number normalization  
  - Automatic separation of "No Hit" records into dedicated files  

---

## 🏗️ Technical Architecture

### 📂 Project Structure

| Component | Description |
|-----------|-------------|
| `run.py` | Main application entry point |
| `main/` | Core application logic (main.py, main02.py, main03.py) |
| `ui/` | Graphical interface built with tkinter + ttkbootstrap |
| `utils/` | Modular utilities for merging, converting, subtracting, and cleaning |
| `pipeline/` | High-level workflow automation scripts |
| `prompts/` | Development documentation and internal workflow logic |

---

### ⚙️ Technologies Used

- **Programming Language:** Python 3.x  
- **GUI Framework:** tkinter with ttkbootstrap  
- **Data Processing:** pandas  
- **Excel Handling:** openpyxl, xlsxwriter  
- **Concurrency:** threading for responsive UI during heavy processing  

---

## 🎯 Use Cases

- **Real Estate Marketing**  
  Prepare skip-traced datasets for cold calling and SMS campaigns.

- **Data Cleaning & Standardization**  
  Normalize inconsistent datasets from multiple lead providers.

- **CRM Data Preparation**  
  Generate ready-to-import datasets for GoHighLevel and similar CRM platforms.

- **Database Management**  
  Merge, de-duplicate, and maintain large property record databases efficiently.

---

## 📄 Summary

AI-Excel-Processing-Tools is a complete data automation framework designed to handle complex Excel and CSV workflows with speed, accuracy, and scalability. Its modular pipelines, advanced utilities, and modern desktop interface make it an essential solution for professionals dealing with high-volume marketing and real estate datasets.
