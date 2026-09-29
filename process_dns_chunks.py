import pandas as pd
import time

# --- KONFIGURASI ---
file_input = "sample-dns-30min.csv"
file_output = "filtered-dns-sample.csv" 
chunk_size = 1_000_000  # Membaca per 1 Juta baris agar aman untuk RAM

# Tentukan hanya kolom yang penting untuk dimuat. Hal ini SANGAT menghemat RAM.
kolom_penting = ['ts_iso', 'src_ip', 'dst_ip', 'qr', 'qname', 'qtype_name', 'rcode']

print(f"Mulai memproses file: {file_input}")
start_time = time.time()

# Akumulator untuk menghitung statistik umum
total_baris = 0
tipe_query_counts = pd.Series(dtype=int)
domain_counts = pd.Series(dtype=int)

# Persiapkan file output untuk di-append jika anda ingin menyimpan data sub-set (filtered data)
# pd.DataFrame(columns=kolom_penting).to_csv(file_output, index=False)

try:
    # Membaca dengan chunking (mencicil) iterasi
    for i, chunk in enumerate(pd.read_csv(file_input, usecols=kolom_penting, chunksize=chunk_size)):
        total_baris += len(chunk)
        
        # --- 1. CONTOH FILTERING: Ambil hanya rekaman Query (Bukan response)
        # qr == 0 (Query), qr == 1 (Response)
        queries_only = chunk[chunk['qr'] == 0]
        
        # JIKA ingin menyimpan hasil filter ke CSV berukuran kecil (Uncomment 2 baris di bawah)
        # queries_only.to_csv(file_output, mode='a', header=False, index=False)
        
        # --- 2. CONTOH AGREGASI (Menghitung Statistik) ---
        # Hitung sebaran tipe record DNS (A, AAAA, NS, dsb)
        qtype_chunk = queries_only['qtype_name'].value_counts()
        tipe_query_counts = tipe_query_counts.add(qtype_chunk, fill_value=0)
        
        # Hitung jumlah domain yang paling sering di-query
        # Gunakan dropna & lowercase agar formatnya rapi
        qname_series = queries_only['qname'].dropna().str.lower()
        qname_chunk = qname_series.value_counts()
        
        domain_counts = domain_counts.add(qname_chunk, fill_value=0)
        # Limitasi agar dictionary ini tidak menumpuk memenuhi RAM (kita simpan top-50,000 saja per rotasi)
        domain_counts = domain_counts.nlargest(50_000)

        print(f"-> Selesai memproses chunk {i+1} : {total_baris:,} baris...")

    # Urutkan hasil akhir
    tipe_query_counts = tipe_query_counts.sort_values(ascending=False).astype(int)
    domain_counts = domain_counts.nlargest(20).astype(int)

    end_time = time.time()
    
    # Menampilkan Rekapitulasi
    print("\n" + "="*40)
    print("HASIL ANALISIS FILE (MENGGUNAKAN CHUNK)")
    print("="*40)
    print(f"Total Baris Diproses : {total_baris:,} baris")
    print(f"Total Waktu Eksekusi : {end_time - start_time:.2f} detik")
    
    print("\n--- Top 5 Tipe Query ---")
    print(tipe_query_counts.head(5).to_string())
    
    print("\n--- Top 20 Domain Paling Sering Di-Query ---")
    print(domain_counts.head(20).to_string())
    print("="*40)

except Exception as e:
    print(f"Terjadi kesalahan: {e}")
