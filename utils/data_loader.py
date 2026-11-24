import pandas as pd
import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

def _load_csv(filename: str) -> pd.DataFrame:
    file_path = BASE_DIR / filename
    if not file_path.exists():
        st.error(f"Không tìm thấy file dữ liệu tại: `{file_path}`. Vui lòng kiểm tra thư mục `data/processed/`.")
        st.stop()
        
    df = pd.read_csv(file_path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
    if "Year" in df.columns:
        df["Year"] = df["Year"].astype(int)
    if "Month" in df.columns:
        df["Month"] = df["Month"].astype(int)
    if "Group_Code" in df.columns:
        df["Group_Code"] = df["Group_Code"].astype(str)
    return df

@st.cache_data
def load_overall_data() -> pd.DataFrame:
    """Đọc dữ liệu CPI chung (CPI_ALL) giai đoạn 01/2020 - 10/2026."""
    df = _load_csv("cpi_overall.csv")
    return df.sort_values("Date").reset_index(drop=True)

@st.cache_data
def load_categories_data() -> pd.DataFrame:
    """Đọc dữ liệu 11 nhóm hàng hóa & dịch vụ chính (G01 - G11) giai đoạn 01/2020 - 10/2026."""
    df = _load_csv("cpi_categories.csv")
    return df.sort_values(["Group_Code", "Date"]).reset_index(drop=True)

@st.cache_data
def load_summary_data() -> pd.DataFrame:
    """Đọc bảng thống kê tổng hợp toàn kỳ."""
    return _load_csv("cpi_summary.csv")