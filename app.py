import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Cấu hình giao diện rộng và tiêu đề trang
st.set_page_config(
    page_title="Chạm là chốt - Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Áp dụng một chút CSS để tùy chỉnh giao diện tối giống ảnh mẫu hơn
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #eceff4; }
    div[data-testid="stMetric"] {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
    </style>
""", unsafe_allow_html=True)
@st.cache_data
def load_data():
    # Đọc file CSV
    df = pd.read_csv("Demo 6 - Sheet1.csv")
    
    # TỰ ĐỘNG SỬA LỖI: Xóa khoảng trắng thừa ở đầu/cuối tên tất cả các cột
    df.columns = df.columns.str.strip()
    
    # Kiểm tra xem có cột thời gian nào chứa chữ "Thời điểm" không để tự chọn
    col_time = [c for c in df.columns if 'Thời điểm' in c]
    if col_time:
        target_col = col_time[0]
        df[target_col] = pd.to_datetime(df[target_col], errors='coerce')
        df['Giờ'] = df[target_col].dt.strftime('%H:00')
    else:
        # Nếu hoàn toàn không tìm thấy thì tự tạo cột Giờ giả lập để không bị sập web
        df['Giờ'] = '00:00'
        
    return df
# 2. Đọc dữ liệu từ file CSV bạn đã tải lên cùng thư mục
@st.cache_data
def load_data():
    # Đọc file và xử lý thời gian
    df = pd.read_csv("Demo 6 - Sheet1.csv")
    df['Thời điểm bắn tin'] = pd.to_datetime(df['Thời điểm bắn tin'], errors='coerce')
    df['Giờ'] = df['Thời điểm bắn tin'].dt.strftime('%H:00')
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Không tìm thấy file 'Demo 6 - Sheet1.csv'. Bạn hãy đảm bảo đã upload file này lên cùng thư mục trên GitHub nhé!")
    st.stop()

# --- TIÊU ĐỀ CHÍNH ---
st.title("Chạm là chốt")
st.caption("Nhật ký báo cáo dữ liệu trực tiếp luồng Chạm là chốt")
st.write("---")

# 3. TÍNH TOÁN CÁC CHỈ SỐ (KPIs)
tong_tin = len(df)
gui_thanh_cong = len(df[df['Trạng thái'].str.upper() == 'SUCCESS']) if 'Trạng thái' in df.columns else tong_tin
ty_le_tc = (gui_thanh_cong / tong_tin * 100) if tong_tin > 0 else 0

# Đếm tổng số người nhận thực tế (Xử lý chuỗi dạng "Email +3 người" nếu có)
tong_doi_tuong = tong_tin # Mặc định nếu không tách chuỗi phức tạp

# Xác định kênh chính
kenh_chinh = df['Kênh nhận'].mode()[0] if 'Kênh nhận' in df.columns else "FPT Chat + Email"

# --- HIỂN THỊ 4 THẺ CHỈ SỐ ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="SỐ TIN ĐÃ BÁN", value=f"{tong_tin}")
with col2:
    st.metric(label="GỬI THÀNH CÔNG", value=f"{gui_thanh_cong}", delta=f"{ty_le_tc:.1f}% Tỷ lệ TC")
with col3:
    st.metric(label="TỔNG SỐ ĐỐI TƯỢNG NHẬN", value=f"{tong_doi_tuong}")
with col4:
    st.metric(label="KÊNH NHẬN CHÍNH", value=kenh_chinh)

st.write("")

# 4. THANH TÌM KIẾM VÀ BỘ LỌC
search_query = st.text_input("🔍 Tìm kiếm theo email, bộ phận, nội dung...", "")

# Lọc dữ liệu theo từ khóa tìm kiếm
if search_query:
    mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
    df_filtered = df[mask]
else:
    df_filtered = df

# 5. BẢNG DANH SÁCH CHI TIẾT
st.subheader("Danh sách chi tiết")
st.dataframe(
    df_filtered[['Thời điểm bắn tin', 'Đối tượng nhận', 'Bộ phận', 'Kênh nhận', 'Trạng thái', 'Xem trước nội dung']], 
    use_container_width=True,
    hide_index=True
)

st.write("---")

# 6. KHU VỰC BIỂU ĐỒ (DƯỚI CÙNG)
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    st.subheader("Tần suất gửi tin theo thời gian")
    if 'Giờ' in df_filtered.columns:
        df_timeline = df_filtered.groupby('Giờ').size().reset_index(name='Số lượng tin')
        df_timeline = df_timeline.sort_values('Giờ')
        
        fig1 = px.line(
            df_timeline, x='Giờ', y='Số lượng tin',
            markers=True,
            template="plotly_dark"
        )
        fig1.update_traces(line_color='#00b4d8', marker=dict(size=8))
        fig1.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Thời gian (Giờ trong ngày)",
            yaxis_title="Số lượng"
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Không có dữ liệu thời gian phù hợp.")

with col_chart2:
    st.subheader("Top 5 bộ phận nhận tin nhiều nhất")
    if 'Bộ phận' in df_filtered.columns:
        df_dept = df_filtered['Bộ phận'].value_counts().reset_index(name='Số lượng')
        df_dept.columns = ['Bộ phận', 'Số lượng']
        df_dept = df_dept.head(5).sort_values('Số lượng', ascending=True) # Sắp xếp để thanh dài nằm trên
        
        fig2 = px.bar(
            df_dept, x='Số lượng', y='Bộ phận',
            orientation='h',
            template="plotly_dark"
        )
        fig2.update_traces(marker_color='#00fa9a')
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Số lượng tin nhận",
            yaxis_title="Bộ phận"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Không có dữ liệu Bộ phận.")
