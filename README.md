# 📊 Vietnam Price Watch – Interactive CPI Monitoring Dashboard

Dashboard tương tác theo dõi, trực quan hóa và phân tích diễn biến Chỉ số Giá tiêu dùng (CPI) tại Việt Nam giai đoạn **01/2020 – 10/2026**, tập trung vào sự phân hóa biến động giá giữa **11 nhóm hàng hóa và dịch vụ tiêu dùng chính**.

## 🎯 Mục tiêu & Phạm vi
- **Phạm vi dữ liệu:** CPI chung (`CPI_ALL`) và 11 nhóm hàng hóa, dịch vụ chính (`G01` – `G11`) theo tháng từ `01/2020` đến `10/2026` (82 kỳ quan sát).
- **Nguồn dữ liệu:** Tổng hợp từ báo cáo thống kê của Cục Thống kê Việt Nam (NSO).
- **Các chức năng chính:**
  1. **CPI Overview (`1_CPI_Overview.py`):** KPI cards tổng quan, bộ lọc khoảng năm, biểu đồ diễn biến các chỉ tiêu `YoY (%)`, `MoM (%)`, `CPI_YoY`, `CPI_MoM`, `Base_2024` và `CPI_YTD`.
  2. **Category Comparison (`pages/2_Category_Comparison.py`):** Biểu đồ đường so sánh xu hướng đa nhóm, biểu đồ cột xếp hạng theo kỳ, bản đồ nhiệt (Heatmap) biến động và bảng dữ liệu chi tiết cho phép tải xuống (`.csv`).
  3. **Inflation Insights (`pages/3_Inflation_Insights.py`):** Điểm nhấn kỳ mới nhất, ma trận phân loại đặc tính biến động (Scatter Plot), phân tích mức đóng góp vào lạm phát giai đoạn 2020–2025 (theo quyền số NSO) và 5 phát hiện trọng tâm.

## 📁 Cấu trúc thư mục
```text
vietnam-price-watch/
├── 1_CPI_Overview.py            # Trang 1: Tổng quan CPI chung
├── pages/
│   ├── 2_Category_Comparison.py # Trang 2: So sánh 11 nhóm hàng hóa & dịch vụ
│   └── 3_Inflation_Insights.py  # Trang 3: Phân tích & Nhận định chuyên sâu
├── data/
│   ├── raw/                     # Dữ liệu gốc (DATASET.xlsx)
│   └── processed/               # Dữ liệu đã làm sạch & chuẩn hóa (.csv)
├── utils/
│   └── data_loader.py           # Hàm đọc và cache dữ liệu
└── requirements.txt             # Danh sách thư viện Python