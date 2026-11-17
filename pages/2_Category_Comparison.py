import streamlit as st
import plotly.express as px
from utils.data_loader import load_cpi_data

# 1. Cấu hình trang
st.set_page_config(
    page_title="Vietnam Price Watch | Category Comparison",
    page_icon="📈",
    layout="wide"
)

# 2. Tải dữ liệu
df = load_cpi_data()

if "is_mock_data" in df.columns and df["is_mock_data"].any():
    st.info("⚠️ **Chế độ kiểm thử giao diện:** Hệ thống đang sử dụng dữ liệu giả lập (`cpi_sample.csv`) mô phỏng cấu trúc chuẩn NSO.")

st.title("📈 So sánh biến động giữa 11 nhóm hàng hóa & dịch vụ")
st.markdown("Phân tích sự phân hóa mức tăng giá và tính mùa vụ giữa các nhóm hàng trong rổ CPI Việt Nam.")
st.divider()

# Lọc bỏ CPI chung (mã 00), chỉ giữ lại 11 nhóm hàng hóa (mã 01 -> 11)
df_cats = df[df["category_code"] != "00"].copy()
df_cats["label"] = df_cats["category_code"] + " - " + df_cats["category_name"]

# 3. Bộ lọc trên Sidebar
st.sidebar.header("Bộ lọc so sánh nhóm hàng")

min_year = int(df_cats["year"].min())
max_year = int(df_cats["year"].max())
year_range = st.sidebar.slider(
    "Chọn khoảng năm:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

metric_choice = st.sidebar.selectbox(
    "Chọn chỉ tiêu phân tích:",
    options=[
        "Tốc độ tăng cùng kỳ năm trước - YoY (%)",
        "Tốc độ tăng so với tháng trước - MoM (%)",
        "Chỉ số giá tiêu dùng - CPI Index"
    ]
)

metric_map = {
    "Tốc độ tăng cùng kỳ năm trước - YoY (%)": ("yoy", "YoY (%)"),
    "Tốc độ tăng so với tháng trước - MoM (%)": ("mom", "MoM (%)"),
    "Chỉ số giá tiêu dùng - CPI Index": ("cpi_index", "Chỉ số CPI")
}
col_name, unit_label = metric_map[metric_choice]

all_labels = sorted(df_cats["label"].unique())
default_labels = [
    lbl for lbl in all_labels
    if lbl.startswith(("01 -", "04 -", "07 -", "09 -"))
]

selected_labels = st.sidebar.multiselect(
    "Chọn nhóm hàng hiển thị trên biểu đồ đường:",
    options=all_labels,
    default=default_labels
)

# Lọc dữ liệu theo năm
df_filtered_year = df_cats[
    (df_cats["year"] >= year_range[0]) &
    (df_cats["year"] <= year_range[1])
].copy()

if df_filtered_year.empty:
    st.warning("Không có dữ liệu trong khoảng thời gian đã chọn.")
    st.stop()

# 4. Biểu đồ 1: Biểu đồ đường so sánh xu hướng các nhóm đã chọn
st.subheader(f"1. Xu hướng {unit_label} theo thời gian giữa các nhóm được chọn")

if not selected_labels:
    st.warning("Vui lòng chọn ít nhất 1 nhóm hàng ở thanh bộ lọc bên trái để hiển thị biểu đồ đường.")
else:
    df_line = df_filtered_year[df_filtered_year["label"].isin(selected_labels)]
    fig_line = px.line(
        df_line,
        x="date",
        y=col_name,
        color="label",
        labels={"date": "Thời gian", col_name: unit_label, "label": "Nhóm hàng hóa"},
        title=f"So sánh diễn biến {metric_choice} ({year_range[0]} – {year_range[1]})"
    )
    if col_name in ["mom", "yoy"]:
        fig_line.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.6)
    fig_line.update_layout(
        hovermode="x unified",
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="left", x=0)
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# 5. Biểu đồ 2 & 3: Xếp hạng 11 nhóm tại kỳ mới nhất & Heatmap biến động
latest_date = df_filtered_year["date"].max()
latest_period_str = latest_date.strftime("%m/%Y")

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader(f"2. Xếp hạng 11 nhóm tại kỳ {latest_period_str}")
    df_rank = df_filtered_year[df_filtered_year["date"] == latest_date].sort_values(col_name, ascending=True)
    
    # Tô màu phân biệt tăng/giảm (nếu là YoY hoặc MoM)
    if col_name in ["mom", "yoy"]:
        df_rank["Trạng thái"] = df_rank[col_name].apply(lambda x: "Tăng (+)" if x >= 0 else "Giảm (-)")
        color_discrete_map = {"Tăng (+)": "#EF553B", "Giảm (-)": "#00CC96"}
        fig_bar = px.bar(
            df_rank,
            x=col_name,
            y="label",
            orientation="h",
            color="Trạng thái",
            color_discrete_map=color_discrete_map,
            text=col_name,
            labels={col_name: unit_label, "label": ""},
            title=f"Xếp hạng {unit_label} tháng {latest_period_str}"
        )
    else:
        fig_bar = px.bar(
            df_rank,
            x=col_name,
            y="label",
            orientation="h",
            text=col_name,
            labels={col_name: unit_label, "label": ""},
            title=f"Xếp hạng {unit_label} tháng {latest_period_str}"
        )

    fig_bar.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_bar.update_layout(height=480, showlegend=False, margin=dict(r=40))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("3. Bản đồ nhiệt (Heatmap) biến động theo thời gian")
    # Tạo bảng pivot cho Heatmap (hàng = nhóm hàng, cột = tháng/năm)
    df_heat = df_filtered_year.copy()
    df_heat["period"] = df_heat["date"].dt.strftime("%Y-%m")
    pivot_heat = df_heat.pivot(index="label", columns="period", values=col_name)
    
    # Đảo ngược thứ tự hàng để nhóm 01 nằm trên cùng
    pivot_heat = pivot_heat.sort_index(ascending=False)

    fig_heat = px.imshow(
        pivot_heat,
        labels=dict(x="Thời gian", y="", color=unit_label),
        color_continuous_scale="RdYlBu_r" if col_name in ["mom", "yoy"] else "Blues",
        aspect="auto",
        title=f"Heatmap {unit_label} của 11 nhóm ({year_range[0]} – {year_range[1]})"
    )
    fig_heat.update_layout(height=480)
    st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# 6. Bảng dữ liệu chi tiết & Tải xuống
st.subheader("4. Bảng dữ liệu chi tiết theo nhóm hàng")

display_df = df_filtered_year[df_filtered_year["label"].isin(selected_labels if selected_labels else all_labels)].copy()
display_df["Tháng/Năm"] = display_df["date"].dt.strftime("%m/%Y")

cols_to_show = ["Tháng/Năm", "category_code", "category_name", "weight", "cpi_index", "mom", "yoy"]
rename_cols = {
    "category_code": "Mã nhóm",
    "category_name": "Tên nhóm hàng hóa, dịch vụ",
    "weight": "Quyền số (%)",
    "cpi_index": "Chỉ số CPI",
    "mom": "MoM (%)",
    "yoy": "YoY (%)"
}

table_clean = display_df[cols_to_show].rename(columns=rename_cols).sort_values(["Tháng/Năm", "Mã nhóm"], ascending=[False, True])

st.dataframe(table_clean, use_container_width=True, hide_index=True)

# Nút tải file CSV
csv_data = table_clean.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    label="📥 Tải xuống bảng dữ liệu này (.CSV)",
    data=csv_data,
    file_name=f"vietnam_cpi_categories_{year_range[0]}_{year_range[1]}.csv",
    mime="text/csv"
)

st.caption("📌 **Nguồn dữ liệu:** Cục Thống kê Việt Nam (NSO) - Dữ liệu mô phỏng cấu trúc MVP.")