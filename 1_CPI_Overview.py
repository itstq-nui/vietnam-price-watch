import streamlit as st
import plotly.express as px
from utils.data_loader import load_overall_data

# 1. Cấu hình trang chính
st.set_page_config(
    page_title="Vietnam Price Watch | CPI Overview",
    page_icon="📊",
    layout="wide"
)

# 2. Tải dữ liệu CPI chung
df = load_overall_data()

# 3. Tiêu đề & Giới thiệu
st.title("📊 Vietnam Price Watch")
st.markdown("**Hệ thống theo dõi, trực quan hóa và phân tích diễn biến Chỉ số Giá tiêu dùng (CPI) Việt Nam (01/2020 – 10/2026)**")
st.divider()

# 4. Bộ lọc trên Sidebar
st.sidebar.header("Bộ lọc dữ liệu")
min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

year_range = st.sidebar.slider(
    "Chọn khoảng năm phân tích:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

df_filtered = df[
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1])
].copy()

if df_filtered.empty:
    st.warning("Không có dữ liệu trong khoảng thời gian đã chọn.")
    st.stop()

# 5. Hàng KPI Cards (lấy tại kỳ mới nhất trong khoảng lọc)
latest_row = df_filtered.iloc[-1]
latest_period = latest_row["Date"].strftime("%m/%Y")
avg_yoy = df_filtered["YoY_Pct"].mean()

st.subheader(f"Chỉ số CPI chung tại kỳ gần nhất trong khoảng lọc ({latest_period})")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Tăng/giảm so với tháng trước (MoM)",
        value=f"{latest_row['MoM_Pct']:+.2f}%",
        delta=f"Chỉ số: {latest_row['CPI_MoM']:.2f}",
        delta_color="off"
    )
with col2:
    st.metric(
        label="Tăng/giảm cùng kỳ năm trước (YoY)",
        value=f"{latest_row['YoY_Pct']:+.2f}%",
        delta=f"Chỉ số: {latest_row['CPI_YoY']:.2f}",
        delta_color="off"
    )
with col3:
    st.metric(
        label=f"Lạm phát YoY bình quân ({year_range[0]}–{year_range[1]})",
        value=f"{avg_yoy:.2f}%"
    )
with col4:
    # Chỉ hiển thị CPI_YTD và Base_2024 khi kỳ gần nhất thuộc năm 2026 (có dữ liệu)
    if latest_row["Year"] == 2026 and not df_filtered["CPI_YTD"].isna().all():
        ytd_pct = latest_row["CPI_YTD"] - 100
        st.metric(
            label=f"So với T12/2025 (YTD {latest_period})",
            value=f"{ytd_pct:+.2f}%",
            delta=f"Gốc 2024 = 100: {latest_row['Base_2024']:.2f}",
            delta_color="off"
        )
    else:
        st.metric(
            label="Chỉ số kỳ gốc 2024 (Base_2024)",
            value="Không áp dụng",
            delta="Chỉ công bố từ năm 2026",
            delta_color="off"
        )

st.divider()

# 6. Biểu đồ diễn biến CPI theo thời gian
st.subheader("Diễn biến CPI chung theo thời gian")

# Xây dựng danh sách chỉ tiêu linh hoạt theo khoảng năm người dùng chọn
metric_options = [
    "Tốc độ tăng cùng kỳ năm trước - YoY (%)",
    "Tốc độ tăng so với tháng trước - MoM (%)",
    "Chỉ số CPI so với cùng kỳ năm trước (Cùng kỳ = 100)",
    "Chỉ số CPI so với tháng trước (Tháng trước = 100)"
]

# Nếu khoảng lọc có chứa năm 2026, mở thêm 2 chỉ tiêu của năm 2026
has_2026_data = not df_filtered["Base_2024"].isna().all()
if has_2026_data:
    metric_options.extend([
        "Chỉ số CPI kỳ gốc 2024 - Base_2024 (Chỉ có từ 2026)",
        "Chỉ số CPI so với tháng 12 năm trước - CPI_YTD (Chỉ có từ 2026)"
    ])

metric_choice = st.radio(
    "Chọn chỉ tiêu hiển thị trên biểu đồ:",
    options=metric_options,
    horizontal=True
)

metric_map = {
    "Tốc độ tăng cùng kỳ năm trước - YoY (%)": ("YoY_Pct", "Tỷ lệ (%)", 0),
    "Tốc độ tăng so với tháng trước - MoM (%)": ("MoM_Pct", "Tỷ lệ (%)", 0),
    "Chỉ số CPI so với cùng kỳ năm trước (Cùng kỳ = 100)": ("CPI_YoY", "Điểm chỉ số", 100),
    "Chỉ số CPI so với tháng trước (Tháng trước = 100)": ("CPI_MoM", "Điểm chỉ số", 100),
    "Chỉ số CPI kỳ gốc 2024 - Base_2024 (Chỉ có từ 2026)": ("Base_2024", "Điểm chỉ số (2024=100)", 100),
    "Chỉ số CPI so với tháng 12 năm trước - CPI_YTD (Chỉ có từ 2026)": ("CPI_YTD", "Điểm chỉ số (T12/2025=100)", 100)
}
col_name, y_label, ref_line = metric_map[metric_choice]

plot_df = df_filtered.dropna(subset=[col_name]).copy()

fig = px.line(
    plot_df,
    x="Date",
    y=col_name,
    markers=True,
    labels={"Date": "Thời gian", col_name: y_label},
    title=f"Diễn biến {metric_choice} ({plot_df['Date'].min().strftime('%m/%Y')} – {plot_df['Date'].max().strftime('%m/%Y')})"
)

fig.add_hline(y=ref_line, line_dash="dash", line_color="gray", opacity=0.6)
fig.update_layout(hovermode="x unified", height=450)
st.plotly_chart(fig, use_container_width=True)

if not has_2026_data:
    st.caption("ℹ️ *Ghi chú: Chỉ số CPI kỳ gốc 2024 (`Base_2024`) và chỉ số so với tháng 12 năm trước (`CPI_YTD`) chỉ được Cục Thống kê công bố từ năm 2026.*")

# 7. Thông tin nguồn dữ liệu
st.caption(f"📌 **Kỳ dữ liệu mới nhất:** Tháng 10/2026 | **Nguồn dữ liệu:** Cục Thống kê Việt Nam (NSO) – Tổng hợp chuỗi số liệu 01/2020 – 10/2026.")