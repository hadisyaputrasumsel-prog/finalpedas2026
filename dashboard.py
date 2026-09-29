import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="PeDaS 2026 DNS Analytics", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS FOR BEAUTIFUL UI ---
st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    .sidebar .sidebar-content { background: #ffffff; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA (CACHED FOR PERFORMANCE) ---
@st.cache_data(ttl=3600)
def load_data(file_buffer, nrows=1_000_000, is_parquet=False):
    # Only load required columns for memory efficiency
    kolom = ['ts_iso', 'ip_ver', 'proto', 'qr', 'qname', 'qtype_name', 'rcode']
    
    try:
        if is_parquet:
            df = pd.read_parquet(file_buffer, columns=kolom)
            if len(df) > nrows:
                df = df.head(nrows)
        else:
            df = pd.read_csv(file_buffer, usecols=kolom, nrows=nrows)
            
        # Preprocessing
        df['ts_iso'] = pd.to_datetime(df['ts_iso'], errors='coerce')
        df['qname'] = df['qname'].fillna('').astype(str).str.lower().replace('nan', '')
        df['domain_len'] = df['qname'].str.len()
        # Create helper columns
        df['qr_label'] = df['qr'].map({0: 'Query', 1: 'Response'})
        df['rcode_label'] = df['rcode'].map(lambda x: "Success (0)" if x == 0 else ("NXDOMAIN (3)" if x == 3 else f"Other ({x})"))
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}. Pastikan file valid dan memiliki kolom yang sesuai.")
        return pd.DataFrame()

# --- SIDEBAR & FILTERING ---
st.sidebar.image("https://img.icons8.com/color/150/000000/dns.png", width=100)
st.sidebar.title("Filter Data")
st.sidebar.markdown("Atur parameter untuk mengeksplorasi data trafik DNS.")

uploaded_file = st.sidebar.file_uploader("Upload File DNS (.csv)", type=["csv"])

nrows_option = st.sidebar.select_slider("Jumlah Data Ditampilkan (Baris x 1000)", options=[100, 500, 1000, 2000], value=500)
st.sidebar.caption("Semakin besar data, semakin lama proses pemuatan.")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tips Business Analytics:** Analisis kegagalan resolusi (NXDOMAIN) yang berlebihan bisa menjadi indikasi potensi botnet atau aktivitas DGA (Domain Generation Algorithm).")

# Retrieve data
parquet_dir = "dns_parquet"
data_path = "sample-dns-30min.csv"
data = pd.DataFrame()

if os.path.exists(parquet_dir) and os.path.isdir(parquet_dir) and len(os.listdir(parquet_dir)) > 0:
    st.sidebar.success(f"✅ Data Tersedia ({parquet_dir} terkompresi)")
    with st.spinner('Memuat Data DNS dari Parquet di server...'):
        data = load_data(parquet_dir, nrows=nrows_option * 1000, is_parquet=True)

elif uploaded_file is not None:
    with st.spinner("Menyimpan file ke server secara otomatis untuk akses nanti..."):
        with open(data_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ File berhasil disimpan di server!")
    
    with st.spinner('Memuat Data DNS dari file yang baru diupload...'):
        data = load_data(data_path, nrows=nrows_option * 1000)

elif os.path.exists(data_path):
    st.sidebar.success(f"✅ Data Tersedia ({data_path})")
    with st.spinner('Memuat Data DNS dari server...'):
        data = load_data(data_path, nrows=nrows_option * 1000)

else:
    st.info("👋 Selamat Datang! Belum ada data di server. Karena ukuran data sangat besar (2.4 GB), silakan upload data yang sudah dikompres menjadi Parquet, atau upload CSV Anda. Jika jaringan tidak stabil, aplikasi ini sudah mendukung format Dataset Parquet yang sangat ringan dari folder 'dns_parquet'.")
    st.stop()

if data.empty:
    st.error("Data kosong atau gagal dimuat.")
    st.stop()

# --- MAIN DASHBOARD HEADER ---
st.title("📡 PeDaS 2026: DNS Traffic Analytics")
st.markdown("Dashboard cerdas untuk memantau performa, keamanan, dan distribusi akses trafik DNS.")

# --- METRIC CARDS ---
col1, col2, col3, col4 = st.columns(4)
total_requests = len(data)
total_queries = len(data[data['qr'] == 0])
total_responses = len(data[data['qr'] == 1])
nxdomain_count = len(data[(data['qr'] == 1) & (data['rcode'] == 3)])

col1.markdown(f'<div class="metric-card"><h3>Total Trafik</h3><h2>{total_requests:,}</h2></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="metric-card"><h3>Total Query</h3><h2>{total_queries:,}</h2></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="metric-card"><h3>Total Response</h3><h2>{total_responses:,}</h2></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="metric-card" style="border-left: 5px solid #e74c3c;"><h3>NXDOMAIN (Gagal)</h3><h2 style="color:#e74c3c;">{nxdomain_count:,}</h2></div>', unsafe_allow_html=True)

# --- TABS FOR DIFFERENT VIEW ---
tab1, tab2, tab3 = st.tabs(["📊 Analisis Trafik & Jaringan", "🌐 Analisis Domain", "📋 Raw Data"])

with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Tren Trafik DNS Per Menit")
        traffic_time = data.groupby(data['ts_iso'].dt.floor('Min')).size().reset_index(name='Jumlah')
        fig_time = px.line(traffic_time, x='ts_iso', y='Jumlah', markers=True, color_discrete_sequence=['#2ecc71'])
        fig_time.update_layout(xaxis_title="Waktu", yaxis_title="Volume Paket", margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_time, use_container_width=True)
        
        st.subheader("Protokol Transportasi")
        fig_proto = px.pie(data, names='proto', hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
        fig_proto.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_proto, use_container_width=True)

    with col_b:
        st.subheader("Distribusi Status Respons (RCODE)")
        df_resp = data[data['qr'] == 1]
        fig_rcode = px.histogram(df_resp, x='rcode_label', color='rcode_label', 
                                color_discrete_map={"Success (0)": "#3498db", "NXDOMAIN (3)": "#e74c3c"})
        fig_rcode.update_layout(xaxis_title="Status Respons", yaxis_title="Frekuensi", showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_rcode, use_container_width=True)
        
        st.subheader("Proporsi Trafik: Query vs Response")
        fig_qr = px.pie(data, names='qr_label', color='qr_label', 
                        color_discrete_map={"Query": "#9b59b6", "Response": "#f1c40f"})
        fig_qr.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_qr, use_container_width=True)

with tab2:
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.subheader("Top 15 Domain Paling Dicari")
        # Ensure we only pick queries for counting domain requests
        top_domains = data[data['qr'] == 0]['qname'].value_counts().head(15).reset_index()
        top_domains.columns = ['Domain', 'Jumlah Request']
        fig_domain = px.bar(top_domains, x='Jumlah Request', y='Domain', orientation='h', color='Jumlah Request', color_continuous_scale='Blues')
        fig_domain.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_domain, use_container_width=True)
        
    with col_d:
        st.subheader("Top Tipe Query DNS Diberikan")
        top_qtypes = data['qtype_name'].value_counts().head(10).reset_index()
        top_qtypes.columns = ['Tipe Query', 'Jumlah']
        fig_qtype = px.bar(top_qtypes, x='Tipe Query', y='Jumlah', color='Tipe Query', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_qtype.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        st.plotly_chart(fig_qtype, use_container_width=True)

    st.subheader("Distribusi Panjang Nama Domain (Karakter)")
    df_len = data[(data['qr'] == 0) & (data['domain_len'] > 0)]
    fig_len = px.histogram(df_len, x='domain_len', nbins=50, color_discrete_sequence=['purple'])
    fig_len.update_layout(xaxis_title="Panjang Karakter", yaxis_title="Hitungan (Log scale)", yaxis_type="log")
    st.plotly_chart(fig_len, use_container_width=True)

with tab3:
    st.subheader("📄 Dataset DNS (Sampel)")
    st.dataframe(data.head(100), use_container_width=True)
    st.caption("Menampilkan 100 baris pertama dari data yang dimuat untuk tinjauan.")
