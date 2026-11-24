import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_overall_data, load_categories_data, load_summary_data

# 1. Cấu hình trang
st.set_page_config(
    page_title="Vietnam Price Watch | Inflation Insights",
    page_icon="💡",
    layout="wide"
)

# 2. Tải dữ liệu
df_overall = load_overall_data()
df_cats = load_categories_data()
df_summary = load_summary_data()

# Tách riêng 11 nhóm hàng trong bảng summary
df_sum_11 = df_summary[df_summary["Group_Code"] != "CPI_ALL"].copy()
df_sum_11["Short_Label"] = df_sum_11["Group_Code"] + " - " + df_sum_11["Category_Name"]

st.title("💡 Phân tích & Nhận định chuyên sâu (Inflation Insights)")
st.markdown("Tổng hợp các phát hiện trọng tâm về động lực tăng giá, đặc tính biến động và mức độ tác động của 11 nhóm hàng hóa, dịch vụ giai đoạn **01/2020 – 10/2026**.")
st.divider()

# ==============================================================================
# KHỐI 1: ĐIỂM NHẤN TẠI KỲ DỮ LIỆU MỚI NHẤT (THÁNG 10/2026)
# ==============================================================================
latest_date = df_cats["Date"].max()
latest_period_str = latest_date.strftime("%m/%Y")
df_latest = df_cats[df_cats["Date"] == latest_date].copy()

top_mom = df_latest.loc[df_latest["MoM_Pct"].idxmax()]
bot_mom = df_latest.loc[df_latest["MoM_Pct"].idxmin()]
top_yoy = df_latest.loc[df_latest["YoY_Pct"].idxmax()]
top_ytd = df_sum_11.loc[df_sum_11["YTD_10M_2026_Pct"].idxmax()]

st.subheader(f"1. Điểm nhấn biến động giá tại kỳ mới nhất ({latest_period_str})")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(
        label="Tăng mạnh nhất tháng (MoM)",
        value=f"{top_mom['MoM_Pct']:+.2f}%",
        delta=f"{top_mom['Group_Code']} - {top_mom['Category_Name']}",
        delta_color="off"
    )
with c2:
    st.metric(
        label="Giảm sâu nhất tháng (MoM)",
        value=f"{bot_mom['MoM_Pct']:+.2f}%",
        delta=f"{bot_mom['Group_Code']} - {bot_mom['Category_Name']}",
        delta_color="off"
    )
with c3:
    st.metric(
        label="Tăng cao nhất cùng kỳ (YoY)",
        value=f"{top_yoy['YoY_Pct']:+.2f}%",
        delta=f"{top_yoy['Group_Code']} - {top_yoy['Category_Name']}",
        delta_color="off"
    )
with c4:
    st.metric(
        label="Tăng cao nhất 10T/2026 (YTD)",
        value=f"{top_ytd['YTD_10M_2026_Pct']:+.2f}%",
        delta=f"{top_ytd['Group_Code']} - {top_ytd['Category_Name']}",
        delta_color="off"
    )

st.divider()

# ==============================================================================
# KHỐI 2: MA TRẬN ĐẶC TÍNH BIẾN ĐỘNG & TỐC ĐỘ TĂNG DÀI HẠN (2020 – 2026)
# ==============================================================================
st.subheader("2. Phân loại đặc tính biến động của 11 nhóm hàng (01/2020 – 10/2026)")

col_chart, col_explain = st.columns([1.4, 1])

with col_chart:
    mean_yoy_all = df_sum_11["Mean_YoY_2020_2026_Pct"].mean()
    mean_std_all = df_sum_11["Std_MoM_Pct"].mean()

    fig_scatter = px.scatter(
        df_sum_11,
        x="Mean_YoY_2020_2026_Pct",
        y="Std_MoM_Pct",
        size="Weight_2020_2025_Pct",
        color="Short_Label",
        text="Group_Code",
        hover_name="Category_Name",
        hover_data={
            "Group_Code": False,
            "Short_Label": False,
            "Mean_YoY_2020_2026_Pct": ":.2f",
            "Std_MoM_Pct": ":.2f",
            "Weight_2020_2025_Pct": ":.2f"
        },
        labels={
            "Mean_YoY_2020_2026_Pct": "Tốc độ tăng YoY bình quân 2020–2026 (%)",
            "Std_MoM_Pct": "Độ biến động MoM - Độ lệch chuẩn (%)",
            "Weight_2020_2025_Pct": "Quyền số 2020–2025 (%)"
        },
        title="Tương quan giữa Mức tăng bình quân (YoY) và Độ biến động (Std MoM)"
    )
    fig_scatter.update_traces(textposition="top center")
    fig_scatter.add_vline(x=mean_yoy_all, line_dash="dash", line_color="gray", opacity=0.5)
    fig_scatter.add_hline(y=mean_std_all, line_dash="dash", line_color="gray", opacity=0.5)
    fig_scatter.update_layout(height=480, showlegend=False)
    st.plotly_chart(fig_scatter, width="stretch")

with col_explain:
    st.markdown("**Cách đọc ma trận (Kích thước bóng = Quyền số rổ CPI):**")
    st.markdown("""
    * **Nhóm tạo áp lực lạm phát nền (Tăng YoY cao, biến động vừa phải):** 
      `G04` (Nhà ở, điện, nước, chất đốt & VLXD: bình quân **+4,41%/năm**) và `G01` (Hàng ăn & dịch vụ ăn uống: **+4,08%/năm**). Do chiếm tổng quyền số hơn **52,38%**, đây là hai trụ cột quyết định mặt bằng lạm phát chung.
    * **Nhóm biến động sốc theo chu kỳ/giá thế giới (Độ lệch chuẩn MoM lớn):** 
      `G07` (Giao thông) có biên độ dao động lớn nhất (**Std = 3,04%**, từng tăng vọt **+12,85%** và giảm sâu **-13,86%** trong một tháng) do phụ thuộc giá xăng dầu. Tiếp theo là `G09` (Giáo dục, **Std = 1,36%**) và `G06` (Thuốc & dịch vụ y tế, **Std = 1,13%**) biến động theo lộ trình điều chỉnh giá dịch vụ công.
    * **Nhóm giảm phát/kìm hãm lạm phát:** 
      `G08` (Thông tin & truyền thông) là nhóm duy nhất có tốc độ tăng bình quân âm (**-0,56%/năm**) nhờ tiến bộ công nghệ và cạnh tranh cước viễn thông.
    """)

st.divider()

# ==============================================================================
# KHỐI 3: PHÂN TÍCH MỨC ĐÓNG GÓP VÀO CPI CHUNG (GIAI ĐOẠN CÓ QUYỀN SỐ 2020–2025)
# ==============================================================================
st.subheader("3. Đóng góp của từng nhóm vào mức tăng CPI bình quân (Giai đoạn 2020–2025)")

st.caption(
    "ℹ️ **Nguyên tắc tính toán:** Mức đóng góp (điểm phần trăm) = `(Tốc độ tăng YoY bình quân × Quyền số) / 100`. "
    "Chỉ tính cho giai đoạn **2020–2025** (nơi có đầy đủ quyền số chính thức của NSO). Giai đoạn năm 2026 không áp dụng quyền số cũ do NSO đã chuyển sang kỳ gốc 2024."
)

df_20_25 = df_cats[(df_cats["Year"] >= 2020) & (df_cats["Year"] <= 2025)].copy()
contrib_df = (
    df_20_25.groupby(["Group_Code", "Category_Name", "Weight_2020_2025"])["YoY_Pct"]
    .mean()
    .reset_index(name="Mean_YoY_20_25")
)
contrib_df["Contribution_pp"] = (contrib_df["Mean_YoY_20_25"] * contrib_df["Weight_2020_2025"] / 100.0).round(2)
contrib_df["Label"] = contrib_df["Group_Code"] + " - " + contrib_df["Category_Name"]
contrib_df = contrib_df.sort_values("Contribution_pp", ascending=True)

fig_contrib = px.bar(
    contrib_df,
    x="Contribution_pp",
    y="Label",
    orientation="h",
    text="Contribution_pp",
    color="Contribution_pp",
    color_continuous_scale="RdYlBu_r",
    labels={"Contribution_pp": "Mức đóng góp bình quân (điểm phần trăm)", "Label": ""},
    title="Đóng góp bình quân của 11 nhóm vào lạm phát YoY giai đoạn 2020–2025 (điểm %)"
)
fig_contrib.update_traces(texttemplate="%{text:+.2f} đpt", textposition="outside")
fig_contrib.update_layout(height=460, coloraxis_showscale=False, margin=dict(r=60))
st.plotly_chart(fig_contrib, width="stretch")

st.divider()

# ==============================================================================
# KHỐI 4: CÁC PHÁT HIỆN TRỌNG TÂM TỪ DỮ LIỆU (KEY INSIGHTS)
# ==============================================================================
st.subheader("4. Các phát hiện trọng tâm từ dữ liệu thống kê (01/2020 – 10/2026)")

with st.expander("📌 Phát hiện 1: Hai nhóm 'Hàng ăn' (G01) và 'Nhà ở & điện nước' (G04) đóng góp hơn 70% mức tăng CPI giai đoạn 2020–2025", expanded=True):
    st.markdown("""
    * **Dẫn chứng số liệu:** Trong giai đoạn 2020–2025, `G01` (quyền số 33,56%) đóng góp bình quân **+1,39 điểm phần trăm** và `G04` (quyền số 18,82%) đóng góp **+0,80 điểm phần trăm** vào mức tăng YoY của CPI chung.
    * **Hàm ý kinh tế:** Dù mức tăng phần trăm hàng tháng của `G01` không đột biến như xăng dầu, nhưng do chiếm tới 1/3 rổ hàng hóa tiêu dùng, mọi biến động theo mùa vụ (đặc biệt dịp Tết Nguyên đán tháng 1–2) của nhóm lương thực, thực phẩm đều tác động trực tiếp đến chỉ số lạm phát toàn nền kinh tế.
    """)

with st.expander("📌 Phát hiện 2: Nhóm 'Giao thông' (G07) là tâm điểm gây nhiễu và đảo chiều CPI trong ngắn hạn", expanded=True):
    st.markdown("""
    * **Dẫn chứng số liệu:** Nhóm `G07` có độ lệch chuẩn biến động tháng cao nhất toàn rổ (**3,04%**), với đỉnh tăng tháng đạt **+12,85%** và đáy giảm sâu tới **-13,86%**. Riêng tại kỳ mới nhất **Tháng 10/2026**, nhóm này ghi nhận mức tăng cùng kỳ lên tới **+15,57% YoY** (và tăng **+15,60%** so với tháng 12/2025), dẫn đầu toàn bộ 11 nhóm hàng.
    * **Hàm ý kinh tế:** Diễn biến CPI nhóm Giao thông phản ánh độ nhạy cực cao của chi phí vận tải trong nước trước biến động giá nhiên liệu thế giới, tạo ra các nhịp tăng/giảm giật cục thay vì xu hướng tuyến tính.
    """)

with st.expander("📌 Phát hiện 3: Tính mùa vụ hành chính rõ nét ở nhóm 'Giáo dục' (G09) và 'Thuốc & dịch vụ y tế' (G06)", expanded=True):
    st.markdown("""
    * **Dẫn chứng số liệu:** Nhóm `G09` ghi nhận mức tăng đột biến theo chu kỳ tựu trường (tháng 8–9 hằng năm) với mức tăng tháng cao nhất đạt **+8,06%**, kéo mức tăng bình quân toàn giai đoạn lên **+3,76%/năm**. Tương tự, nhóm `G06` có độ lệch chuẩn **1,13%** và đỉnh tăng tháng **+9,47%** gắn liền với các đợt điều chỉnh khung giá dịch vụ khám chữa bệnh của Nhà nước.
    * **Hàm ý kinh tế:** Đây là nhóm lạm phát mang tính chất điều tiết và mùa vụ hành chính, giúp phân biệt rõ áp lực tăng giá do chính sách với áp lực tăng giá do cung – cầu thị trường.
    """)

with st.expander("📌 Phát hiện 4: Nhóm 'Thông tin và truyền thông' (G08) đóng vai trò bộ giảm xóc cho rổ CPI", expanded=True):
    st.markdown("""
    * **Dẫn chứng số liệu:** Trong suốt 82 tháng quan sát (01/2020 – 10/2026), `G08` là nhóm duy nhất duy trì tốc độ tăng bình quân âm (**-0,56%/năm YoY** và **-0,04%/tháng MoM**), với biên độ dao động hẹp nhất (**Std = 0,10%**).
    * **Hàm ý kinh tế:** Xu hướng giảm giá thiết bị đầu cuối và các gói cước viễn thông giúp trung hòa một phần áp lực tăng giá từ các nhóm hàng thiết yếu khác.
    """)

with st.expander("📌 Phát hiện 5: Mặt bằng lạm phát năm 2026 có dấu hiệu nhích lên so với giai đoạn 2020–2025", expanded=True):
    st.markdown("""
    * **Dẫn chứng số liệu:** Tính đến tháng **10/2026**, CPI chung tăng **+5,09% YoY** và tăng **+4,41%** so với tháng 12/2025 (cao hơn mức tăng bình quân **3,26%/năm** của toàn chuỗi 2020–2026). Động lực tăng chính trong 10 tháng đầu năm 2026 tập trung ở nhóm `G07` (Giao thông: **+15,60% YTD**), `G04` (Nhà ở & điện nước: **+6,55% YTD**) và `G11` (Hàng hóa & dịch vụ khác: **+5,14% YTD**).
    """)

st.caption("📌 **Nguồn dữ liệu:** Cục Thống kê Việt Nam (NSO) – Tổng hợp và tính toán từ chuỗi dữ liệu chính thức 01/2020 – 10/2026.")