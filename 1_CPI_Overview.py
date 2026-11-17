# Đổi tên/dùng làm Trang chính (Trang 1: CPI Overview)
import streamlit as st
import plotly.express as px
from utils.data_loader import load_cpi_data

# 1. Cấu hình trang chính
st.set_page_config(
    page_title="Vietnam Price Watch | CPI Overview",
    page_icon="📊",
    layout="wide"
)

# 2. Tải dữ liệu
df = load_cpi_data()

# Hiển thị cảnh báo nếu đang dùng dữ liệu mẫu
if "is_mock_data" in df.columns and df["is_mock_data"].any():
    st.info("⚠️ **Chế độ kiểm thử giao diện:** Hệ thống đang sử dụng dữ liệu giả lập (`cpi_sample.csv`) mô phỏng cấu trúc chuẩn NSO. Số liệu chính thức sẽ được cập nhật sau.")

# 3. Tiêu đề & Giới thiệu
st.title("📊 Vietnam Price Watch")
st.markdown("**Hệ thống theo dõi, trực quan hóa và phân tích diễn biến Chỉ số Giá tiêu dùng (CPI) Việt Nam**")
st.divider()

# 4. Bộ lọc trên Sidebar
st.sidebar.header("Bộ lọc dữ liệu")
min_year = int(df["year"].min())
max_year = int(df["year"].max())

year_range = st.sidebar.slider(
    "Chọn khoảng năm phân tích:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Lọc dữ liệu CPI chung (mã 00) theo khoảng năm đã chọn
df_general = df[
    (df["category_code"] == "00") &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
].copy()

if df_general.empty:
    st.warning("Không có dữ liệu trong khoảng thời gian đã chọn.")
    st.stop()

# 5. Hàng KPI Cards (lấy tại kỳ mới nhất trong khoảng lọc)
latest_row = df_general.iloc[-1]
latest_period = latest_row["date"].strftime("%m/%Y")

# Tính bình quân YoY trong kỳ lọc
avg_yoy = df_general["yoy"].mean()

st.subheader(f"Chỉ số CPI chung tại kỳ gần nhất ({latest_period})")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Chỉ số CPI (Gốc 2019 = 100)",
        value=f"{latest_row['cpi_index']:.2f}"
    )
with col2:
    st.metric(
        label="Tăng/giảm so với tháng trước (MoM)",
        value=f"{latest_row['mom']:+.2f}%",
        delta=f"{latest_row['mom']:+.2f}%",
        delta_color="inverse"  # Lạm phát tăng hiển thị màu đỏ cảnh báo
    )
with col3:
    st.metric(
        label="Tăng/giảm cùng kỳ năm trước (YoY)",
        value=f"{latest_row['yoy']:+.2f}%",
        delta=f"{latest_row['yoy']:+.2f}%",
        delta_color="inverse"
    )
with col4:
    st.metric(
        label=f"Lạm phát bình quân ({year_range[0]}–{year_range[1]})",
        value=f"{avg_yoy:.2f}%"
    )

st.divider()

# 6. Biểu đồ diễn biến CPI theo thời gian
st.subheader("Diễn biến CPI chung theo thời gian")

metric_choice = st.radio(
    "Chọn chỉ tiêu hiển thị trên biểu đồ:",
    options=["Tốc độ tăng cùng kỳ năm trước - YoY (%)", "Tốc độ tăng so với tháng trước - MoM (%)", "Chỉ số giá tiêu dùng - CPI Index"],
    horizontal=True
)

metric_map = {
    "Tốc độ tăng cùng kỳ năm trước - YoY (%)": ("yoy", "Tỷ lệ (%)"),
    "Tốc độ tăng so với tháng trước - MoM (%)": ("mom", "Tỷ lệ (%)"),
    "Chỉ số giá tiêu dùng - CPI Index": ("cpi_index", "Điểm chỉ số")
}
col_name, y_label = metric_map[metric_choice]

fig = px.line(
    df_general,
    x="date",
    y=col_name,
    markers=True,
    labels={"date": "Thời gian", col_name: y_label},
    title=f"Diễn biến {metric_choice} giai đoạn {year_range[0]} – {year_range[1]}"
)

# Thêm đường tham chiếu 0% nếu xem MoM hoặc YoY
if col_name in ["mom", "yoy"]:
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.6)

fig.update_layout(hovermode="x unified", height=450)
st.plotly_chart(fig, use_container_width=True)

# 7. Thông tin nguồn dữ liệu
st.caption(f"📌 **Kỳ dữ liệu mới nhất:** Tháng {latest_period} | **Nguồn dữ liệu:** Cục Thống kê Việt Nam (NSO) - Dữ liệu mô phỏng cấu trúc MVP.")