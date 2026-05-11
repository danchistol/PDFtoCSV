# 📄 PDF to CSV Converter

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green?style=for-the-badge)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-black?style=for-the-badge&logo=pandas)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

### 🚀 Convert PDF tables and text into CSV files with a modern Python desktop application.

</div>

---

# ✨ Features

- 📊 Extract tables from PDF files
- 📝 Extract text line-by-line
- 🤖 Automatic extraction mode
- 📁 Export separate and merged CSV files
- ⚡ Fast and lightweight
- 🖥️ User-friendly Tkinter GUI
- 📈 Progress bar and live logs
- 🌍 UTF-8 encoding support
- ⚙️ Custom CSV delimiter support

---

# 🛠️ Built With

- 🐍 Python
- 📄 pdfplumber
- 📊 pandas
- 🖥️ Tkinter

---

# 🚀 Installation

## 1️⃣ Clone the repository

```bash
git clone https://github.com/danchistol/pdf-to-csv-converter.git
cd pdf-to-csv-converter
```

## 2️⃣ Install dependencies

```bash
pip install pdfplumber pandas
```

---

# ▶️ Run the Application

```bash
python PDFtoCSV.py
```

---

# ⚙️ How It Works

1️⃣ Select a PDF file  
2️⃣ Choose the output folder  
3️⃣ Select extraction mode:
- `Auto`
- `Tables`
- `Text`

4️⃣ Click **Convert**  
5️⃣ Access generated CSV files instantly

---

# 🧠 Extraction Modes

| Mode | Description |
|------|-------------|
| Auto | Detects tables automatically and falls back to text extraction |
| Tables | Extracts only tables from the PDF |
| Text | Extracts text line-by-line |

---

# 📂 Output Example

```text
output/
├── tables/
│   ├── page_0001_table_01.csv
│   ├── page_0002_table_01.csv
│
├── tables_merged.csv
└── text_lines.csv
```

---

# 📸 Use Cases

✔ Financial Reports  
✔ Invoices  
✔ Bank Statements  
✔ Research Papers  
✔ Data Migration  
✔ PDF Data Extraction

---

# 🤝 Contributing

Pull requests are welcome. Feel free to fork the repository and submit improvements.

---

# 📜 License

MIT License

---

<div align="center">

Made with ❤️ using Python

</div>
