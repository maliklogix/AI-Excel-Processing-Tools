AI-Excel-Processing-Tools: Comprehensive Project Description
Overview
AI-Excel-Processing-Tools (internally referred to as Hitrotech Data Tools) is a robust, Python-based desktop application designed for high-volume data manipulation, specifically tailored for real estate lead generation and marketing workflows. Built with a modern ttkbootstrap interface, the toolkit provides a centralized dashboard for processing large CSV and Excel datasets through automated pipelines.

The project is structured as an extensible framework, with a core application (main.py) that has been progressively enhanced through main02.py and main03.py. It automates the "list building" process—standardizing raw data, removing duplicates, enriching records with phone numbers, and formatting outputs for CRM platforms like GoHighLevel (GHL).


Key Features
1. Advanced Data Pipelines
The application includes specialized pipelines for different data types:

Bulk List Builder: A comprehensive pipeline for processing MCHB MPV and 6-phone vacant lot lists.
AAE List Builder: Specifically designed for AAE lists, featuring automated 3-phone enrichment and Step01 toggle capabilities.
Resident Data Pipeline: Processes resident-specific data with support for up to 6 phone numbers.
Vacant Lot Pipeline: Generates vacant lot lists with detailed property and mailing information.
2. Core Utility Tools
Smart Separator: Splits large files into smaller datasets based on unique column values (e.g., separating by County or Zip Code).
Advanced File Merger: Combines multiple CSV or Excel files into a single unified workbook with key column alignment and record summaries.
Record Subtractor: Compares two datasets and removes overlapping records based on composite keys, essential for avoiding duplicate marketing efforts.
Column Mapper & Adder: Features an interactive UI to map source columns to standard schemas and inject new data from master files into target folders recursively.
Record Collector: Recursively searches through directory structures to collect specific folder types (e.g., "GHL Ready", "SkipTraced") into a central repository.
3. Format Conversion & Standardization
Bi-directional Conversion: Seamlessly convert between CSV and Excel (XLSX) formats while preserving data types like ZIP codes and phone numbers.
GHL Compiler: Reshapes data into "GHL Ready" format, expanding multiple phone numbers into individual rows to comply with CRM import requirements.
Standardization: Automatically applies Pascal case to addresses and cities, normalizes phone formats, and handles "No Hit" records by separating them into dedicated files.


Technical Architecture
Project Structure
Component
Description
run.py
The main entry point that initializes the application.
main/
Contains the core application logic across three versions (main.py, main02.py, main03.py).
ui/
Implements the graphical interface using tkinter and ttkbootstrap.
utils/
A collection of modular scripts for specific tasks like merging, converting, and subtracting.
pipeline/
High-level scripts that coordinate multiple utilities to perform complex workflows.
prompts/
Documentation of the development process and logic used to build the tools.

Technologies Used
Language: Python 3.x
GUI Framework: tkinter with ttkbootstrap (for modern, responsive themes).
Data Processing: pandas (for high-performance data manipulation).
File Handling: openpyxl and xlsxwriter (for advanced Excel operations).
Concurrency: threading (to keep the UI responsive during heavy processing).


Use Cases
Real Estate Marketing: Preparing skip-traced lists for cold calling or SMS campaigns.
Data Cleaning: Standardizing inconsistent data from multiple lead sources.
CRM Preparation: Formatting datasets specifically for GoHighLevel or similar platforms.
Database Management: Merging and de-duplicating large property record databases.

