# AI Invoice OCR System

A Python-based invoice automation app using **PyMuPDF, Tesseract OCR, pandas, and Streamlit**. It extracts invoice fields from documents and exports a structured Excel report through a Traditional Chinese interface.

## Features
- Upload multiple PDF, JPG, PNG, or TXT invoices
- Extract text from PDFs and use Tesseract OCR for scanned pages and images
- Parse labelled invoice number, date, vendor, and total fields
- Flag missing fields and isolate per-file errors
- Preview results and export to Excel

## Tech Stack
Python · PyMuPDF · Tesseract OCR · pandas · Streamlit · openpyxl · pytest

## Project Structure
```text
ai-invoice-ocr-system/
├── app.py
├── invoice_ocr/
│   ├── __init__.py
│   └── core.py
├── sample_data/
├── tests/
│   └── test_core.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Quick Start
Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) for scanned images/PDFs; ensure `tesseract` is on PATH. Install its `chi_tra` language data for Traditional Chinese OCR.

```bash
pip install -r requirements.txt
streamlit run app.py
```
Upload the included TXT samples to try the workflow without Tesseract.

## Testing
```bash
python -m pytest -q
```

## Limitations
- Rule-based extraction works best on clearly labelled invoices; complex layouts need further work.
- `OK` only means required fields were found, not verified.
- Local OCR quality depends on image resolution and installed language data.
- Sample invoices contain fictional data.
