"""Traditional Chinese Streamlit interface for local invoice OCR."""
import streamlit as st
from invoice_ocr.core import process_files, to_excel

st.set_page_config(page_title="發票 OCR 自動化處理系統", page_icon="🧾", layout="wide")
st.title("🧾 發票 OCR 自動化處理系統")
st.caption("PDF／圖片文字辨識 × 發票欄位擷取 × Excel 報表")

with st.sidebar:
    st.header("辨識設定")
    lang = st.selectbox("OCR 辨識語言", ["eng", "eng+chi_tra"], format_func=lambda x: "英文" if x == "eng" else "英文＋繁體中文", help="繁體中文辨識需安裝 Tesseract chi_tra 語言套件。")
    st.caption("圖片與掃描型 PDF 必須先安裝 Tesseract OCR。純文字檔與文字型 PDF 可直接處理。")

st.subheader("1. 上傳發票")
uploads = st.file_uploader("選擇一個或多個發票檔案", type=["pdf", "png", "jpg", "jpeg", "txt"], accept_multiple_files=True)
st.caption("支援 PDF、PNG、JPG、TXT；可以先使用 sample_data 中的文字範例測試。")
if st.button("開始辨識與驗證", type="primary", disabled=not uploads):
    with st.spinner("正在擷取文字、辨識欄位並產生報表…"):
        st.session_state["invoice_results"] = process_files([(f.name, f.getvalue()) for f in uploads], lang=lang)
    st.success("處理完成！")

if "invoice_results" in st.session_state:
    df = st.session_state["invoice_results"]
    st.divider()
    st.subheader("2. 處理結果")
    a, b, c = st.columns(3)
    a.metric("處理檔案數", len(df))
    b.metric("欄位齊全（OK）", int((df.status == "OK").sum()))
    c.metric("待確認／失敗", int((df.status != "OK").sum()))
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("OK：必要欄位已找到；REVIEW：欄位缺漏；ERROR：檔案處理失敗。OK 不代表發票資料已核實。")
    st.download_button("📥 下載 Excel 報表", data=to_excel(df), file_name="invoice_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
