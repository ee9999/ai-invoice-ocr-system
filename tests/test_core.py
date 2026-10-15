from invoice_ocr.core import parse_invoice, process_files, to_excel

SAMPLE = "Invoice Number: INV-2026-001\nDate: 2026-10-01\nVendor: Demo Store\nTotal: TWD 1,250.00"

def test_parse_invoice():
    row = parse_invoice(SAMPLE, "demo.txt")
    assert row["invoice_number"] == "INV-2026-001"
    assert row["total"] == 1250.0
    assert row["status"] == "OK"

def test_missing_field_requires_review():
    assert parse_invoice("Vendor: Demo")["status"] == "REVIEW"

def test_batch_error_isolated():
    df = process_files([("demo.txt", SAMPLE.encode()), ("bad.xyz", b"x")])
    assert df.iloc[0]["status"] == "OK"
    assert df.iloc[1]["status"].startswith("ERROR")
    assert to_excel(df)[:2] == b"PK"
