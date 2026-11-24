import streamlit as st
import plotly.express as px
from utils.data_loader import load_categories_data

# 1. Cấu hình trang
st.set_page_config(
    page_title="Vietnam Price Watch | Category Comparison",
    page_icon="📈",
    layout="wide"
)

# 2. Tải dữ liệu 11 nhóm hàng
df_cats = load_categories_data()

st.title("📈 So sánh biến động giữa 11 nhóm hàng hóa & dịch vụ")
st.markdown("Phân tích sự phân hóa mức tăng giá, biên độ dao động và tính mùa vụ giữa 11 nhóm hàng tiêu dùng chính (01/2020 – 10/2026).")
st.divider()

df_cats["Label"] = df_cats["Group_Code"] + " - " + df_cats["Category_Name"]

# 3. Bộ lọc trên Sidebar
st.sidebar.header("Bộ lọc so sánh nhóm hàng")

min_year = int(df_cats["Year"].min())
max_year = int(df_cats["Year"].max())
year_range = st.sidebar.slider(
    "Chọn khoảng năm:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

df_filtered_year = df_cats[
    (df_cats["Year"] >= year_range[0]) &
    (df_cats["Year"] <= year_range[1])
].copy()

if df_filtered_year.empty:
    st.warning("Không có dữ liệu trong khoảng thời gian đã chọn.")
    st.stop()

metric_options = [
    "Tốc độ tăng cùng kỳ năm trước - YoY (%)",
    "Tốc độ tăng so với tháng trước - MoM (%)",
    "Chỉ số CPI so với cùng kỳ năm trước (Cùng kỳ = 100)",
    "Chỉ số CPI so với tháng trước (Tháng trước = 100)"
]

has_2026_data = not df_filtered_year["Base_2024"].isna().all()
if has_2026_data:
    metric_options.extend([
        "Chỉ số CPI kỳ gốc 2024 - Base_2024 (Chỉ có từ 2026)",
        "Chỉ số CPI so với tháng 12 năm trước - CPI_YTD (Chỉ có từ 2026)"
    ])

metric_choice = st.sidebar.selectbox(
    "Chọn chỉ tiêu phân tích:",
    options=metric_options
)

metric_map = {
    "Tốc độ tăng cùng kỳ năm trước - YoY (%)": ("YoY_Pct", "YoY (%)", 0),
    "Tốc độ tăng so với tháng trước - MoM (%)": ("MoM_Pct", "MoM (%)", 0),
    "Chỉ số CPI so với cùng kỳ năm trước (Cùng kỳ = 100)": ("CPI_YoY", "CPI YoY", 100),
    "Chỉ số CPI so với tháng trước (Tháng trước = 100)": ("CPI_MoM", "CPI MoM", 100),
    "Chỉ số CPI kỳ gốc 2024 - Base_2024 (Chỉ có từ 2026)": ("Base_2024", "Base 2024", 100),
    "Chỉ số CPI so với tháng 12 năm trước - CPI_YTD (Chỉ có từ 2026)": ("CPI_YTD", "CPI YTD", 100)
}
col_name, unit_label, ref_line = metric_map[metric_choice]

all_labels = sorted(df_cats["Label"].unique())
default_labels = [
    lbl for lbl in all_labels
    if lbl.startswith(("G01 -", "G04 -", "G07 -", "G09 -"))
]

selected_labels = st.sidebar.multiselect(
    "Chọn nhóm hàng hiển thị trên biểu đồ đường:",
    options=all_labels,
    default=default_labels
)

# Lọc bỏ các dòng NaN của chỉ tiêu đang chọn (ví dụ khi chọn Base_2024 sẽ tự lọc lấy năm 2026)
df_metric = df_filtered_year.dropna(subset=[col_name]).copy()

# 4. Biểu đồ 1: Biểu đồ đường so sánh xu hướng các nhóm đã chọn
st.subheader(f"1. Xu hướng {unit_label} theo thời gian giữa các nhóm được chọn")

if not selected_labels:
    st.warning("Vui lòng chọn ít nhất 1 nhóm hàng ở thanh bộ lọc bên trái để hiển thị biểu đồ đường.")
else:
    df_line = df_metric[df_metric["Label"].isin(selected_labels)]
    fig_line = px.line(
        df_line,
        x="Date",
        y=col_name,
        color="Label",
        labels={"Date": "Thời gian", col_name: unit_label, "Label": "Nhóm hàng hóa"},
        title=f"So sánh diễn biến {metric_choice} ({df_line['Date'].min().strftime('%m/%Y')} – {df_line['Date'].max().strftime('%m/%Y')})"
    )
    fig_line.add_hline(y=ref_line, line_dash="dash", line_color="gray", opacity=0.6)
    fig_line.update_layout(
        hovermode="x unified",
        height=460,
        legend=dict(orientation="h", yanchor="bottom", y=-0.45, xanchor="left", x=0)
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# 5. Biểu đồ 2 & 3: Xếp hạng 11 nhóm tại kỳ mới nhất & Heatmap biến động
latest_date = df_metric["Date"].max()
latest_period_str = latest_date.strftime("%m/%Y")

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader(f"2. Xếp hạng 11 nhóm tại kỳ {latest_period_str}")
    df_rank = df_metric[df_metric["Date"] == latest_date].sort_values(col_name, ascending=True)

    if col_name in ["MoM_Pct", "YoY_Pct"]:
        df_rank["Trạng thái"] = df_rank[col_name].apply(lambda x: "Tăng (+)" if x >= 0 else "Giảm (-)")
        fig_bar = px.bar(
            df_rank,
            x=col_name,
            y="Label",
            orientation="h",
            color="Trạng thái",
            color_discrete_map={"Tăng (+)": "#EF553B", "Giảm (-)": "#00CC96"},
            text=col_name,
            labels={col_name: unit_label, "Label": ""},
            title=f"Xếp hạng {unit_label} tháng {latest_period_str}"
        )
    else:
        fig_bar = px.bar(
            df_rank,
            x=col_name,
            y="Label",
            orientation="h",
            text=col_name,
            labels={col_name: unit_label, "Label": ""},
            title=f"Xếp hạng {unit_label} tháng {latest_period_str}"
        )

    fig_bar.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_bar.update_layout(height=500, showlegend=False, margin=dict(r=50))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("3. Bản đồ nhiệt (Heatmap) biến động theo thời gian")
    df_heat = df_metric.copy()
    df_heat["Period"] = df_heat["Date"].dt.strftime("%Y-%m")
    pivot_heat = df_heat.pivot(index="Label", columns="Period", values=col_name).sort_index(ascending=False)

    fig_heat = px.imshow(
        pivot_heat,
        labels=dict(x="Thời gian", y="", color=unit_label),
        color_continuous_scale="RdYlBu_r" if col_name in ["MoM_Pct", "YoY_Pct"] else "Blues",
        aspect="auto",
        title=f"Heatmap {unit_label} của 11 nhóm ({df_metric['Date'].min().strftime('%m/%Y')} – {latest_period_str})"
    )
    fig_heat.update_layout(height=500)
    st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# 6. Bảng dữ liệu chi tiết & Tải xuống
st.subheader("4. Bảng dữ liệu chi tiết theo nhóm hàng")

display_df = df_filtered_year[df_filtered_year["Label"].isin(selected_labels if selected_labels else all_labels)].copy()
display_df["Kỳ báo cáo"] = display_df["Date"].dt.strftime("%m/%Y")

cols_to_show = ["Kỳ báo cáo", "Group_Code", "Category_Name", "Weight_2020_2025", "MoM_Pct", "YoY_Pct", "CPI_MoM", "CPI_YoY", "CPI_YTD", "Base_2024"]
rename_cols = {
    "Group_Code": "Mã nhóm",
    "Category_Name": "Tên nhóm hàng hóa, dịch vụ",
    "Weight_2020_2025": "Quyền số 20-25 (%)",
    "MoM_Pct": "MoM (%)",
    "YoY_Pct": "YoY (%)",
    "CPI_MoM": "CPI MoM",
    "CPI_YoY": "CPI YoY",
    "CPI_YTD": "CPI YTD (2026)",
    "Base_2024": "Base 2024 (2026)"
}

table_clean = display_df[cols_to_show].rename(columns=rename_cols).sort_values(["Kỳ báo cáo", "Mã nhóm"], ascending=[False, True])

# Hiển thị dạng format đẹp, ẩn bớt chữ NaN thành dấu "-" cho dễ đọc
st.dataframe(
    table_clean.style.format({
        "Quyền số 20-25 (%)": "{:.2f}",
        "MoM (%)": "{:+.2f}",
        "YoY (%)": "{:+.2f}",
        "CPI MoM": "{:.2f}",
        "CPI YoY": "{:.2f}",
        "CPI YTD (2026)": "{:.2f}",
        "Base 2024 (2026)": "{:.2f}"
    }, na_rep="—"),
    use_container_width=True,
    hide_index=True
)

csv_data = table_clean.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    label="📥 Tải xuống bảng dữ liệu này (.CSV)",
    data=csv_data,
    file_name=f"vietnam_cpi_categories_{year_range[0]}_{year_range[1]}.csv",
    mime="text/csv"
)

st.caption("📌 **Nguồn dữ liệu:** Cục Thống kê Việt Nam (NSO) – Tổng hợp chuỗi số liệu 01/2020 – 10/2026. Dấu `—` biểu thị chỉ tiêu không công bố trong giai đoạn tương ứng.")