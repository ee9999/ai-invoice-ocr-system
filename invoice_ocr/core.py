from pathlib import Path
import io
import re
import pandas as pd

FIELDS = ["invoice_number", "date", "vendor", "total", "currency", "status", "source"]

def extract_text(filename: str, content: bytes, lang: str = "eng") -> str:
    """Read PDF text layer; OCR empty PDF pages and images using local Tesseract."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        return content.decode("utf-8-sig")
    if suffix == ".pdf":
        import fitz
        pages = []
        with fitz.open(stream=content, filetype="pdf") as doc:
            for page in doc:
                text = page.get_text("text").strip()
                if not text:
                    import pytesseract
                    pytesseract.pytesseract.tesseract_cmd = (r"D:\Program Files\Tesseract-OCR\tesseract.exe")
                    from PIL import Image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    image = Image.open(io.BytesIO(pix.tobytes("png")))
                    text = pytesseract.image_to_string(image, lang=lang).strip()
                pages.append(text)
        return "\n".join(pages)
    if suffix in (".png", ".jpg", ".jpeg"):
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = (r"D:\Program Files\Tesseract-OCR\tesseract.exe")
        from PIL import Image, ImageOps
        img = Image.open(io.BytesIO(content)).convert("RGB")
        img = ImageOps.autocontrast(img)
        return pytesseract.image_to_string(img, lang=lang)
    raise ValueError("Supported formats: PDF, PNG, JPG, TXT")

def parse_invoice(text: str, source: str = "") -> dict:
    """Deterministic extraction for explicitly labelled English demo invoices.
    Not a general-purpose receipt parser; review fields before business use.
    """
    patterns = {
        "invoice_number": r"(?im)^\s*(?:invoice\s*(?:no\.?|number|#)|發票號碼)\s*[:：]\s*(\S[^\r\n]*)",
        "date": r"(?im)^\s*(?:date|invoice\s*date|日期)\s*[:：]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
        "vendor": r"(?im)^\s*(?:vendor|supplier|seller|店家)\s*[:：]\s*(\S[^\r\n]*)",
        "total": r"(?im)^\s*(?:grand\s*total|total\s*amount|total|總計)\s*[:：]\s*(?:(USD|TWD|NTD|EUR)\s*)?\$?\s*([\d,]+(?:\.\d{1,2})?)\s*(USD|TWD|NTD|EUR)?\s*$",
    }
    row = {k: "" for k in FIELDS}
    row["source"] = source
    for key in ("invoice_number", "date", "vendor"):
        match = re.search(patterns[key], text)
        if match:
            row[key] = match.group(1).strip()
    match = re.search(patterns["total"], text)
    if match:
        row["currency"] = (match.group(1) or match.group(3) or "").upper()
        row["total"] = float(match.group(2).replace(",", ""))
    if row["date"]:
        date = pd.to_datetime(row["date"], errors="coerce")
        row["date"] = date.strftime("%Y-%m-%d") if not pd.isna(date) else ""
    row["status"] = "OK" if all(row.get(k) not in ("", None) for k in ("invoice_number", "date", "vendor", "total")) else "REVIEW"
    return row

def process_files(files: list[tuple[str, bytes]], lang="eng") -> pd.DataFrame:
    rows = []
    for name, content in files:
        try:
            row = parse_invoice(extract_text(name, content, lang), name)
        except Exception as exc:
            row = {k: "" for k in FIELDS}
            row.update(source=name, status=f"ERROR: {type(exc).__name__}: {exc}")
        rows.append(row)
    return pd.DataFrame(rows, columns=FIELDS)

def to_excel(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Invoices")
    return buffer.getvalue()
