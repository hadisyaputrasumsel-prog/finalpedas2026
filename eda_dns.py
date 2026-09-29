import pandas as pd
import matplotlib.pyplot as plt
import os

# --- KONFIGURASI ---
file_input = "sample-dns-30min.csv"
output_dir = "EDA_Results"
os.makedirs(output_dir, exist_ok=True)

print(f"Membaca 2 Juta baris dari file '{file_input}' ...")
kolom = ['ts_iso', 'ip_ver', 'proto', 'qr', 'qname', 'qtype_name', 'rcode']
df = pd.read_csv(file_input, usecols=kolom, nrows=2_000_000)

print("Melakukan persiapan data...")
# Konversi data tipe datetime
df['ts_iso'] = pd.to_datetime(df['ts_iso'], errors='coerce')
df['qname'] = df['qname'].fillna('').astype(str).str.lower().replace('nan', '')

# Hitung panjang domain
df['domain_len'] = df['qname'].str.len()

print("Mengekstrak Grafik EDA...")

# 1. Keseimbangan Trafik (Query vs Response)
plt.figure(figsize=(6, 5))
df['qr_label'] = df['qr'].map({0: 'Query (0)', 1: 'Response (1)'})
df['qr_label'].value_counts().plot(kind='bar', color=['#3498db', '#e74c3c'])
plt.title('Proporsi Trafik: Query vs Response', fontsize=12, fontweight='bold')
plt.ylabel('Total Paket')
plt.xticks(rotation=0)
plt.savefig(f"{output_dir}/01_query_vs_response.png", dpi=150)
plt.close()

# 2. Analisis NXDOMAIN (Keberhasilan Resolusi DNS)
plt.figure(figsize=(8, 5))
df_resp = df[df['qr'] == 1]
rcodes = df_resp['rcode'].value_counts()
rcodes.plot(kind='bar', color='orange')
plt.title('Distribusi Response Code (RCODE)\n(0=Sukses, 3=Gagal/NXDOMAIN)', fontsize=12, fontweight='bold')
plt.xlabel('Kode RCODE')
plt.ylabel('Frekuensi')
plt.xticks(rotation=0)
plt.savefig(f"{output_dir}/02_rcode_distribution.png", dpi=150)
plt.close()

# 3. Top 15 Akses Domain Tertinggi
plt.figure(figsize=(10, 6))
top_domains = df[df['qr'] == 0]['qname'].value_counts().head(15)
top_domains.plot(kind='barh', color='teal').invert_yaxis()
plt.title('Top 15 Domain Paling Sering Di-Query', fontsize=12, fontweight='bold')
plt.xlabel('Jumlah Query')
plt.ylabel('Domain')
plt.tight_layout()
plt.savefig(f"{output_dir}/03_top_15_domains.png", dpi=150)
plt.close()

# 4. Distribusi Panjang Nama Domain
plt.figure(figsize=(8, 5))
df_len = df[(df['qr'] == 0) & (df['domain_len'] > 0)]['domain_len']
df_len.plot(kind='hist', bins=60, color='purple', alpha=0.7)
plt.title('Distribusi Panjang Karakter Domain', fontsize=12, fontweight='bold')
plt.xlabel('Jumlah Karakter Pada Domain')
plt.ylabel('Frekuensi (Logarithmic)')
plt.yscale('log')
plt.savefig(f"{output_dir}/04_domain_length_distribution.png", dpi=150)
plt.close()

# 5. Tren Trafik Berdasarkan Waktu
plt.figure(figsize=(12, 5))
traffic_time = df.groupby(df['ts_iso'].dt.floor('Min')).size()
traffic_time.plot(color='#2ecc71', linewidth=2)
plt.title('Volume DNS Trafik Per Menit', fontsize=12, fontweight='bold')
plt.xlabel('Waktu (Menit)')
plt.ylabel('Jumlah Paket')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{output_dir}/05_traffic_over_time.png", dpi=150)
plt.close()

# 6. Protokol
plt.figure(figsize=(6, 5))
df['proto'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['#9b59b6', '#34495e'])
plt.title('Protokol Transport Terpakai', fontweight='bold')
plt.ylabel('')
plt.savefig(f"{output_dir}/06_protocol.png", dpi=150)
plt.close()

# 7. Tipe Query
plt.figure(figsize=(8, 5))
top_qtypes = df['qtype_name'].value_counts().head(7)
top_qtypes.plot(kind='bar', color='coral')
plt.title('Top 7 Tipe Query DNS', fontweight='bold')
plt.ylabel('Frekuensi')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{output_dir}/07_qtypes.png", dpi=150)
plt.close()

print()
print("="*50)
print(f"✅ Proses EDA Selesai!")
print(f"Semua grafik visualisasi telah disimpan di folder: {output_dir}")
print("="*50)
