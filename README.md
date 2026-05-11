# 📄 PDF to CSV Converter

A modern desktop application built with Python that converts PDF documents into structured CSV files quickly and efficiently.

## ✨ Features

### 📊 Table Extraction
Extracts tables from PDF files and exports:
- Individual CSV files for each table
- A merged CSV containing all extracted tables

### 📝 Text Extraction
Extracts readable text line-by-line into CSV format.

### ⚡ Auto Detection Mode
Automatically:
1. Detects tables inside the PDF
2. Falls back to text extraction if no tables are found

### 🖥️ Desktop GUI
Simple and user-friendly interface with:
- 📂 File picker
- 📁 Output folder selection
- 📈 Progress bar
- 📜 Real-time logs

## 🛠️ Technologies Used

- 🐍 Python 3
- 🪟 Tkinter
- 📑 pdfplumber
- 🐼 pandas
