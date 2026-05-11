import csv
import os
import sys
import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pdfplumber
import pandas as pd
import webbrowser

def safe_mkdir(p: Path):
    p.mkdir(parents=True, exist_ok=True)
    return p

def sanitize_filename(name: str) -> str:
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name

def write_tables_incremental(pdf_path: Path, outdir: Path, encoding: str = "utf-8", delimiter: str = ",", log=lambda *_: None) -> int:
    tables_dir = safe_mkdir(outdir / "tables")
    merged_path = outdir / "tables_merged.csv"

    merged_file = merged_path.open("w", newline="", encoding=encoding)
    merged_writer = None
    total_tables = 0

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            try:
                tables = page.extract_tables()
            except Exception as e:
                log(f"[Avertisment] Eroare la extragerea tabelelor pe pagina {page_num}: {e}")
                tables = []

            for t_idx, table in enumerate(tables, start=1):
                max_cols = max((len(r) for r in table if r is not None), default=0)
                norm = []
                for r in table:
                    if r is None:
                        continue
                    row = list(r)
                    if len(row) < max_cols:
                        row += [""] * (max_cols - len(row))
                    norm.append(row)

                df = pd.DataFrame(norm)

                single_name = sanitize_filename(f"page_{page_num:04d}_table_{t_idx:02d}.csv")
                single_path = tables_dir / single_name
                try:
                    df.to_csv(single_path, index=False, header=False, encoding=encoding)
                except Exception as e:
                    log(f"[Avertisment] Nu pot scrie {single_path.name}: {e}")

                if merged_writer is None:
                    header = ["source", "page", "table_index", "row_index"] + [f"col_{i}" for i in range(max_cols)]
                    merged_writer = csv.writer(merged_file, delimiter=delimiter)
                    merged_writer.writerow(header)

                for ridx, row in enumerate(norm):
                    merged_writer.writerow([pdf_path.name, page_num, t_idx, ridx, *[(c if c is not None else "") for c in row]])

                total_tables += 1
                log(f"[Info] Pagina {page_num} – tabel {t_idx} salvat.")

    merged_file.close()
    return total_tables

def write_text_incremental(pdf_path: Path, outdir: Path, encoding: str = "utf-8", delimiter: str = ",", log=lambda *_: None) -> int:
    text_path = outdir / "text_lines.csv"
    total_lines = 0
    with pdfplumber.open(str(pdf_path)) as pdf, text_path.open("w", newline="", encoding=encoding) as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(["source", "page", "line_index", "text"])
        for page_num, page in enumerate(pdf.pages, start=1):
            try:
                text = page.extract_text(x_tolerance=1, y_tolerance=1) or ""
            except Exception as e:
                log(f"[Avertisment] Eroare la extragerea textului pe pagina {page_num}: {e}")
                text = ""
            lines = [ln.strip("\ufeff").strip() for ln in text.splitlines() if ln.strip()]
            for i, ln in enumerate(lines):
                writer.writerow([pdf_path.name, page_num, i, ln])
                total_lines += 1
            log(f"[Info] Pagina {page_num}: {len(lines)} linii.")
    return total_lines

def convert_pdf(pdf_path: Path, outdir: Path, mode: str, delimiter: str, encoding: str, log=lambda *_: None, set_progress=lambda *_: None):
    outdir = safe_mkdir(outdir)
    log(f"[Start] Fișier: {pdf_path.name}")
    log(f"[Info] Director ieșire: {outdir}")
    log(f"[Info] Mod: {mode} | Delimitator: '{delimiter}' | Encoding: {encoding}")

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            total_pages = max(1, len(pdf.pages))
    except Exception as e:
        raise RuntimeError(f"Nu pot deschide PDF-ul: {e}")

    progress_state = {"done_pages": 0}

    def progress_page():
        progress_state["done_pages"] += 1
        set_progress(min(100, int(progress_state["done_pages"] / total_pages * 100)))

    if mode == "tables":
        n = write_tables_incremental(pdf_path, outdir, encoding=encoding, delimiter=delimiter, log=lambda m: (log(m), progress_page()))
        if n == 0:
            log("[Info] Nu am detectat tabele. Poți încerca modul 'text' sau 'auto'.")
    elif mode == "text":
        n = write_text_incremental(pdf_path, outdir, encoding=encoding, delimiter=delimiter, log=lambda m: (log(m), progress_page()))
        log(f"[Ok] Am scris {n} linii de text în {outdir / 'text_lines.csv'}")
    else:
        log("[Info] Mod AUTO: încerc tabele…")
        n_tables = write_tables_incremental(pdf_path, outdir, encoding=encoding, delimiter=delimiter, log=lambda m: (log(m), progress_page()))
        if n_tables > 0:
            log(f"[Ok] Am detectat {n_tables} tabel(e). Vezi {outdir/'tables'} și {outdir/'tables_merged.csv'}.")
        else:
            log("[Info] Nu am găsit tabele. Trec pe modul TEXT…")
            n_lines = write_text_incremental(pdf_path, outdir, encoding=encoding, delimiter=delimiter, log=lambda m: (log(m), progress_page()))
            log(f"[Ok] Am scris {n_lines} linii în {outdir/'text_lines.csv'}")

    set_progress(100)
    log("[Gata] Conversia s-a încheiat.")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF → CSV Converter")
        self.geometry("720x520")
        self.minsize(680, 520)

        self.pdf_path = tk.StringVar()
        self.outdir = tk.StringVar(value=str(Path.cwd() / "pdf_to_csv_output"))
        self.mode = tk.StringVar(value="auto")
        self.delimiter = tk.StringVar(value=",")
        self.encoding = tk.StringVar(value="utf-8")

        self._build_ui()
        self.worker = None

    def _build_ui(self):
        pad = {"padx": 10, "pady": 8}

        frm = ttk.Frame(self)
        frm.pack(fill="x", **pad)

        ttk.Label(frm, text="Fișier PDF:").grid(row=0, column=0, sticky="w")
        e_pdf = ttk.Entry(frm, textvariable=self.pdf_path, width=70)
        e_pdf.grid(row=0, column=1, sticky="we", padx=(6,6))
        ttk.Button(frm, text="Alege…", command=self.choose_pdf).grid(row=0, column=2, sticky="e")

        ttk.Label(frm, text="Folder ieșire:").grid(row=1, column=0, sticky="w")
        e_out = ttk.Entry(frm, textvariable=self.outdir, width=70)
        e_out.grid(row=1, column=1, sticky="we", padx=(6,6))
        ttk.Button(frm, text="Selectează…", command=self.choose_outdir).grid(row=1, column=2, sticky="e")

        opt = ttk.Frame(self)
        opt.pack(fill="x", **pad)

        ttk.Label(opt, text="Mod:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(opt, text="Auto", value="auto", variable=self.mode).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(opt, text="Tables", value="tables", variable=self.mode).grid(row=0, column=2, sticky="w")
        ttk.Radiobutton(opt, text="Text", value="text", variable=self.mode).grid(row=0, column=3, sticky="w")

        ttk.Label(opt, text="Delimitator CSV:").grid(row=0, column=4, sticky="e")
        ttk.Entry(opt, textvariable=self.delimiter, width=4).grid(row=0, column=5, sticky="w", padx=(6,12))
        ttk.Label(opt, text="Encoding:").grid(row=0, column=6, sticky="e")
        ttk.Entry(opt, textvariable=self.encoding, width=10).grid(row=0, column=7, sticky="w", padx=(6,0))

        btns = ttk.Frame(self)
        btns.pack(fill="x", **pad)
        self.btn_run = ttk.Button(btns, text="Convertește", command=self.start_convert)
        self.btn_run.pack(side="left")
        self.btn_open = ttk.Button(btns, text="Deschide folderul", command=self.open_outdir, state="disabled")
        self.btn_open.pack(side="left", padx=(10,0))

        pf = ttk.Frame(self)
        pf.pack(fill="x", **pad)
        self.pb = ttk.Progressbar(pf, mode="determinate", maximum=100)
        self.pb.pack(fill="x")

        lf = ttk.LabelFrame(self, text="Jurnal")
        lf.pack(fill="both", expand=True, **pad)
        self.txt = tk.Text(lf, height=16, wrap="word")
        self.txt.pack(fill="both", expand=True)
        self.txt.configure(state="disabled")

        for i in range(3):
            self.grid_columnconfigure(i, weight=1)

    def log(self, msg: str):
        self.txt.configure(state="normal")
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")
        self.txt.configure(state="disabled")
        self.update_idletasks()

    def set_progress(self, v: int):
        self.pb["value"] = v
        self.update_idletasks()

    def choose_pdf(self):
        path = filedialog.askopenfilename(
            title="Alege fișier PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if path:
            self.pdf_path.set(path)
            try:
                pp = Path(path)
                self.outdir.set(str(pp.parent / (pp.stem + "_CSV")))
            except Exception:
                pass

    def choose_outdir(self):
        path = filedialog.askdirectory(title="Alege folderul de ieșire")
        if path:
            self.outdir.set(path)

    def open_outdir(self):
        try:
            webbrowser.open(Path(self.outdir.get()).as_uri())
        except Exception:
            os.startfile(self.outdir.get())

    def start_convert(self):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("În lucru", "O conversie este deja în curs.")
            return

        pdf = Path(self.pdf_path.get().strip('" '))
        outdir = Path(self.outdir.get().strip('" '))
        if not pdf.exists():
            messagebox.showerror("Eroare", "Te rog alege un fișier PDF valid.")
            return
        if not outdir.exists():
            try:
                outdir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Eroare", f"Nu pot crea folderul de ieșire:\n{e}")
                return

        self.btn_run.configure(state="disabled")
        self.btn_open.configure(state="disabled")
        self.set_progress(0)
        self.txt.configure(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.configure(state="disabled")

        def job():
            try:
                convert_pdf(
                    pdf_path=pdf,
                    outdir=outdir,
                    mode=self.mode.get(),
                    delimiter=self.delimiter.get(),
                    encoding=self.encoding.get(),
                    log=self.log,
                    set_progress=self.set_progress,
                )
                self.btn_open.configure(state="normal")
            except Exception as e:
                self.log("[Eroare] " + str(e))
                self.log(traceback.format_exc())
                messagebox.showerror("Eroare", str(e))
            finally:
                self.btn_run.configure(state="normal")

        self.worker = threading.Thread(target=job, daemon=True)
        self.worker.start()

if __name__ == "__main__":
    app = App()
    app.mainloop()
