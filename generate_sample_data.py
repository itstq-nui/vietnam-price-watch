import pandas as pd
import numpy as np
from pathlib import Path

# Đảm bảo thư mục data/processed tồn tại
output_dir = Path(__file__).parent / "data" / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

# Danh mục 11 nhóm hàng hóa chuẩn NSO (2020 - 2025)
categories = [
    {"code": "01", "name": "Hàng ăn và dịch vụ ăn uống", "weight": 33.56, "base_trend": 0.0028, "vol": 0.004},
    {"code": "02", "name": "Đồ uống và thuốc lá", "weight": 2.73, "base_trend": 0.0018, "vol": 0.002},
    {"code": "03", "name": "May mặc, mũ nón, giày dép", "weight": 5.70, "base_trend": 0.0015, "vol": 0.002},
    {"code": "04", "name": "Nhà ở, điện, nước, chất đốt và VLXD", "weight": 18.82, "base_trend": 0.0032, "vol": 0.005},
    {"code": "05", "name": "Thiết bị và đồ dùng gia đình", "weight": 6.74, "base_trend": 0.0015, "vol": 0.002},
    {"code": "06", "name": "Thuốc và dịch vụ y tế", "weight": 5.39, "base_trend": 0.0020, "vol": 0.003},
    {"code": "07", "name": "Giao thông", "weight": 9.67, "base_trend": 0.0025, "vol": 0.015},
    {"code": "08", "name": "Bưu chính viễn thông", "weight": 3.14, "base_trend": -0.0005, "vol": 0.001},
    {"code": "09", "name": "Giáo dục", "weight": 6.17, "base_trend": 0.0030, "vol": 0.004},
    {"code": "10", "name": "Văn hóa, giải trí và du lịch", "weight": 4.55, "base_trend": 0.0018, "vol": 0.003},
    {"code": "11", "name": "Hàng hóa và dịch vụ khác", "weight": 3.53, "base_trend": 0.0022, "vol": 0.002},
]

# Tạo chuỗi thời gian từ 01/2019 đến 12/2025 (lấy thêm năm 2019 để tính được YoY cho năm 2020)
dates = pd.date_range(start="2019-01-01", end="2025-12-01", freq="MS")
np.random.seed(42)

records = []

# Sinh chỉ số CPI Index (gốc 2019 = 100) cho từng nhóm
for cat in categories:
    index_val = 100.0
    for d in dates:
        # Tạo hiệu ứng mùa vụ thực tế theo đặc điểm từng nhóm
        seasonal = 0.0
        if cat["code"] in ["01", "02"] and d.month in [1, 2]:  # Tết Nguyên đán
            seasonal = 0.008
        elif cat["code"] == "09" and d.month in [8, 9]:  # Mùa tựu trường
            seasonal = 0.015
        elif cat["code"] == "10" and d.month in [5, 6, 7]:  # Du lịch hè
            seasonal = 0.005

        monthly_change = cat["base_trend"] + seasonal + np.random.normal(0, cat["vol"])
        if d > pd.Timestamp("2019-01-01"):
            index_val = index_val * (1 + monthly_change)

        records.append({
            "date": d,
            "year": d.year,
            "month": d.month,
            "category_code": cat["code"],
            "category_name": cat["name"],
            "weight": cat["weight"],
            "cpi_index": round(index_val, 2),
        })

df_cat = pd.DataFrame(records)

# Tính CPI chung theo bình quân gia quyền của 11 nhóm
df_general = (
    df_cat.groupby(["date", "year", "month"])
    .apply(lambda g: np.sum(g["cpi_index"] * g["weight"]) / 100.0)
    .reset_index(name="cpi_index")
)
df_general["cpi_index"] = df_general["cpi_index"].round(2)
df_general["category_code"] = "00"
df_general["category_name"] = "CPI chung"
df_general["weight"] = 100.0

# Gộp CPI chung và 11 nhóm
df_all = pd.concat([df_general, df_cat], ignore_index=True)
df_all = df_all.sort_values(["category_code", "date"]).reset_index(drop=True)

# Tính toán MoM (%) và YoY (%) chuẩn xác từ cpi_index
df_all["mom"] = (df_all.groupby("category_code")["cpi_index"].pct_change(1) * 100).round(2)
df_all["yoy"] = (df_all.groupby("category_code")["cpi_index"].pct_change(12) * 100).round(2)

# Lọc đúng phạm vi dự án: 2020 - 2025
df_final = df_all[df_all["year"] >= 2020].copy()
df_final["date"] = df_final["date"].dt.strftime("%Y-%m-%d")
df_final["is_mock_data"] = True  # Cờ đánh dấu dữ liệu mẫu

# Lưu ra file CSV
output_path = output_dir / "cpi_sample.csv"
df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"Đã tạo thành công file dữ liệu mẫu tại: {output_path} ({len(df_final)} dòng)")
