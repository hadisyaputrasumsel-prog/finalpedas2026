# Analisis Trafik Registri DNS: Identifikasi Anomali dan Mitigasi Risiko Keamanan
**Nama Tim:** [ISI DENGAN NAMA TIM ANDA - DILARANG MENYEBUT ASAL KAMPUS]

## 1. Ringkasan dan Tujuan
**Masalah & Pemangku Kepentingan:** 
Domain Name System (DNS) merupakan pilar utama layanan internet yang sangat sering disalahgunakan oleh *threat actor* untuk melakukan *Phishing*, *DNS Tunneling*, atau *Domain Generation Algorithm (DGA)* berbasis *Malware*. Analisis ini ditujukan bagi **Tim Security Operation Center (SOC)** dan **Administrator Infrastruktur Jaringan**.
**Pertanyaan Analisis:** Bagaimana pola kueri dan frekuensi anomali pada trafik DNS (seperti kegagalan resolusi/NXDOMAIN dan panjang karakter domain abnormal) dapat diidentifikasi dalam kurun waktu layanan singkat untuk menemukan potensi ancaman?
**Keputusan yang Ingin Dibantu:** Membantu tim SOC menetapkan kebijakan *blocking* secara real-time atas aktivitas anomali berulang dan memberikan rekomendasi pembatasan *rate-limit* untuk domain yang dicurigai (misal: botnet).

## 2. Data dan Metode
**Cakupan Data:** Log trafik mentah (Pcap/Data DNS) berdurasi ~30 menit masa padat yang terdiri atas lebih dari 11,7 juta record.
**Unit Analisis:** Analisis ditekankan pada agregat menit `ts_iso`, perilaku respon `rcode`, dan rasio panjang `qname`.
**Pemeriksaan & Preprocessing:**
Disebabkan oleh limitasi memori fisik (ukuran mencapai 2.4 GB), kami menggunakan teknik *Chunking Processing* secara bertahap (1 juta baris per *batch*). Transformasi agregasi difokuskan pada:
- Isolasi trafik *Query (0)* dan *Response (1)*.
- Ekstraksi fitur baru berupa panjang karakter (*Length*) dari nama domain yang diakses.
**Tools yang Digunakan:** Pemrosesan berbasis *Python (Pandas, Matplotlib, Seaborn)* menggunakan teknik EDA terotomasi (*Automated Exploratory Data Analysis*).

## 3. Temuan Utama dan Visualisasi
**Temuan 1: Dominasi Kueri pada Domain Uji Jaringan**
Trafik didominasi oleh akses kueri standar `A` (IPv4) sebanyak 2,08 juta dengan domain pengakses paling membebankan adalah `smartconnect.id` (353 Ribu *hits*), `axarva.id`, dan sub-domain uji kecepatan seperti `speedtest.rndlabbankmandiri.co.id` yang menandakan besarnya lalu lintas alat diagnostik mesin / *automated heartbeat server*.
*(Sertakan Gambar 03_top_15_domains.png di sini)*

**Temuan 2: Potensi Beban Ekstrem Akibat Kegagalan Resolusi NXDOMAIN**
Pada analisis distribusi `RCODE`, kami menemukan porsi yang signifikan pada kemunculan RCODE `3` (NXDOMAIN/Domain Tidak Ditemukan). Resolusi berulang pada domain tak dikenal dengan *string* panjang tak beraturan merepresentasikan indikasi keberadaan algoritme DGA (*Domain Generation Algorithm*) dari infeksi *malware* di sisi internal *client*.
*(Sertakan Gambar 02_rcode_distribution.png dan 04_domain_length_distribution.png di sini)*

**Temuan 3: Ketidakseimbangan Ekstrem Trafik Berbasis Akses Mesin**
Lonjakan (*spike*) trafik pada deret waktu menit-ke-menit tetap statis di angka konstan. Keadaan linear asimetris tanpa bentuk grafik kurva-alamiah menandakan bahwa aktivitas kueri dikirim oleh serangkaian perangkat otomatis / mesin berulang *(cron-bot)* dibanding interaksi organik pengguna otentik.
*(Sertakan Gambar 05_traffic_over_time.png di sini)*

## 4. Rekomendasi dan Keterbatasan
**Rekomendasi Tindakan:**
1. Menerapkan pengawasan agregatif ketat pada IP (DNS *Sinkholing*) yang dalam satu menit me-request lebih dari 100 domain NXDOMAIN secara beruntun.
2. Filter *Policy-based* terhadap sub-domain buatan pihak ke-tiga seperti *speedtest* untuk diturunkan prioritas responnya bila sedang masuk masa puncak (*Peak Hours*) agar utilisasi resoslver tidak terkuras. 

**Keterbatasan:** 
Data hanya merepresentasikan siklus trafik "30 Menit", sehingga analisis pola berulang harian (sirkadian ritmik) *cyber-attack* jangka panjang (seperti serangan APT) tidak bisa divisualisasikan dengan tepat. Tidak tersedianya *Payload* lengkap (seperti rekaman IP *Botnet* global) membuat agregat sumber serangan belum dapat terverifikasi mendalam.

## 5. Pengungkapan dan Akses Hasil
**Penggunaan AI/Pemodelan:** 
Kami mengekslorasi *Large Language Models / Antigravity Agentic AI* murni berfungsi untuk optimasi otomasi sistem sintaksis pada visualisasi *chunking Python (Seaborn)* yang besar tanpa modifikasi dan fabrikasi fiktif data fundamental. Evaluasi logika dan konklusi divalidasi penuh oleh nalar manusia. Referensi lengkap prompt / log kode operasional disertakan pada bagian lampiran (*Appendix*).

**Akses Hasil:** 
*(Hapus sub-judul ini jika Anda tidak mengembangkan Dashboard berbasis URL Publik. Namun jika membuat Dashboard Looker Studio / Tableau, lampirkan URL publiknya di sini)*.

---
*(HALAMAN BERIKUTNYA / LAMPIRAN)*
## Referensi dan Lampiran
* Mockapetris, P. (1987). Domain names - implementation and specification. RFC 1035.
* [Sisipkan Dokumentasi Kode Python 'process_dns_chunks.py' dan Log Penggunaan AI di Sini]
