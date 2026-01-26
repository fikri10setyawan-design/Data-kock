import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Badminton Kock Tracker", page_icon="🏸")

# --- KONEKSI KE GOOGLE SHEETS ---
# Pastikan nama koneksi di secrets.toml kamu adalah "gsheets"
conn = st.connection("gsheets", type=GSheetsConnection)

# Baca data yang sudah ada (Tab 1: Log_Transaksi)
# ttl=0 artinya jangan di-cache, biar datanya selalu fresh
try:
    existing_data = conn.read(worksheet="Log_Transaksi", ttl=0)
    # Bersihkan row yang kosong (kadang ada sisa row kosong dari GSheets)
    existing_data = existing_data.dropna(how="all")
except:
    # Kalau sheet masih kosong/belum ada, bikin dataframe kosong
    existing_data = pd.DataFrame(columns=["Tanggal", "Jam", "Pemain", "Jumlah", "Keterangan"])

# --- HEADER APLIKASI ---
st.title("🏸 Kock Tracker")
st.write("Catat pemakaian kock per game secara real-time.")

# --- DAFTAR PEMAIN (Bisa diedit sesuka hati) ---
list_pemain = ["Fikri", "Nopek", "Diki", "Sigit", "Mang Oco", "Agus", "Fatah", "Kholid", "Riski"]

# --- BAGIAN INPUT (FORM LAPANGAN) ---
with st.container():
    st.subheader("Siapa yang main?")
    
    # Pakai st.form biar halaman gak reload tiap kali pilih nama
    with st.form("form_kock"):
        # Layout 2x2 Lapangan
        col_depan, col_belakang = st.columns(2)
        
        with col_depan:
            st.caption("Tim A (Kiri/Depan)")
            p1 = st.selectbox("Pemain 1", list_pemain, index=0)
            p2 = st.selectbox("Pemain 2", list_pemain, index=1)
            
        with col_belakang:
            st.caption("Tim B (Kanan/Belakang)")
            p3 = st.selectbox("Pemain 3", list_pemain, index=2)
            p4 = st.selectbox("Pemain 4", list_pemain, index=3)

        # Tombol Submit
        submitted = st.form_submit_button("🏸 Submit (+1 Kock)")

        if submitted:
            # 1. Ambil waktu sekarang
            now = datetime.now()
            tgl = now.strftime("%Y-%m-%d")
            jam = now.strftime("%H:%M:%S")

            # 2. Siapkan data baru (4 baris sekaligus)
            pemain_aktif = [p1, p2, p3, p4]
            data_baru_list = []
            
            for p in pemain_aktif:
                data_baru_list.append({
                    "Tanggal": tgl,
                    "Jam": jam,
                    "Pemain": p,
                    "Jumlah": 1,
                    "Keterangan": "Game Rutin"
                })
            
            df_baru = pd.DataFrame(data_baru_list)

            # 3. Gabung data lama + data baru
            # concat is king! ini cara numpuk data di pandas
            updated_df = pd.concat([existing_data, df_baru], ignore_index=True)

            # 4. Kirim balik ke Google Sheets
            conn.update(worksheet="Log_Transaksi", data=updated_df)
            
            st.success(f"Berhasil! 1 Kock dicatat untuk: {', '.join(pemain_aktif)}")
            st.rerun() # Refresh halaman biar tabel di bawah update

# --- BAGIAN REPORT (TABEL KLASEMEN) ---
st.divider()
st.subheader("📊 Klasemen Boros Kock")

if not existing_data.empty:
    # Bikin Pivot Table (Rekap) otomatis pakai Pandas
    # Group by Pemain, lalu jumlahkan kolom "Jumlah"
    rekap = existing_data.groupby("Pemain")["Jumlah"].sum().reset_index()
    
    # Urutkan dari yang paling boros
    rekap_sorted = rekap.sort_values(by="Jumlah", ascending=False)
    
    # Tampilkan tabelnya
    st.dataframe(rekap_sorted, hide_index=True, use_container_width=True)
else:
    st.info("Belum ada data pemakaian. Yuk main!")