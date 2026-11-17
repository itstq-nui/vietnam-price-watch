import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_cpi_data(file_path: str = "data/processed/cpi_sample.csv") -> pd.DataFrame:
    """
    Đọc và kiểm tra tính hợp lệ của bộ dữ liệu CPI.
    Sử dụng @st.cache_data để tối ưu tốc độ tải trang trên Streamlit.
    """
    full_path = Path(__file__).resolve().parent.parent / file_path
    
    if not full_path.exists():
        st.error(f"Không tìm thấy file dữ liệu tại: `{full_path}`. Vui lòng kiểm tra lại đường dẫn.")
        st.stop()
        
    df = pd.read_csv(full_path)
    
    # Chuẩn hóa định dạng thời gian và mã nhóm
    df["date"] = pd.to_datetime(df["date"])
    df["category_code"] = df["category_code"].astype(str).str.zfill(2)
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)
    
    # Sắp xếp chuẩn theo mã nhóm và thời gian
    df = df.sort_values(["category_code", "date"]).reset_index(drop=True)
    return df