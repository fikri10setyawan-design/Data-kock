import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Badminton Kock Tracker", page_icon="🏸")

# --- KONEKSI KE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. BACA DATA STATUS KOCK (Merk & Sisa)
try:
    df_status = conn.read(worksheet="Status_Kock", ttl=0)
    nama_kock_aktif = df_status.iloc[0]["Nama_Kock"]
    sisa_kock = int(df_status.iloc[0]["Sisa"])
    total_isi = int(df_status.iloc[0]["Total_Isi"])
except:
    nama_kock_aktif = "Belum Diset"
    sisa_kock = 0
    total_isi = 12
    df_status = pd.DataFrame([{"Nama_Kock": "Samurai", "Sisa": 12, "Total_Isi": 12}])

# 2. BACA DATA LOG TRANSAKSI
try:
    existing_data = conn.read(worksheet="Log_Transaksi", ttl=0)
    existing_data = existing_data.dropna(how="all")
except:
    existing_data = pd.DataFrame(columns=["Tanggal", "Jam", "Pemain", "Jumlah", "Keterangan"])

# ==========================================
# 1. UI BAGIAN ATAS: MONITOR STOK (HEADER)
# ==========================================
st.title("🏸 Kock Tracker")

col_info1, col_info2 = st.columns(2)
with col_info1:
    st.info(f"📦 **Kock Terpakai:**\n# {nama_kock_aktif}")
with col_info2:
    if sisa_kock <= 2:
        st.error(f"⚠️ **Sisa Kock:**\n# {sisa_kock} / {total_isi}")
    else:
        st.success(f"✅ **Sisa Kock:**\n# {sisa_kock} / {total_isi}")

# ==========================================
# 2. KLASEMEN & RIWAYAT (DIPINDAHKAN KE TENGAH)
# ==========================================
st.write("---")
st.subheader("📊 Statistik & Riwayat")

if not existing_data.empty:
    tab1, tab2 = st.tabs(["Klasemen Total", "Riwayat Match"])
    
    with tab1:
        # Bikin Pivot Table (Rekap) otomatis pakai Pandas
        rekap = existing_data.groupby("Pemain")["Jumlah"].sum().reset_index()
        # Urutkan dari yang paling boros
        rekap_sorted = rekap.sort_values(by="Jumlah", ascending=False)
        # Progress bar style untuk visualisasi
        st.dataframe(
            rekap_sorted, 
            column_config={
                "Jumlah": st.column_config.ProgressColumn(
                    "Total Pemakaian",
                    format="%d",
                    min_value=0,
                    max_value=int(rekap_sorted["Jumlah"].max() if not rekap_sorted.empty else 100),
                )
            },
            hide_index=True, 
            use_container_width=True
        )

    with tab2:
        st.caption("Pertandingan diurutkan dari yang terbaru.")
        # Logic Grouping Match
        # 1. Group by Tanggal & Jam, lalu jadikan list pemain
        df_match = existing_data.groupby(["Tanggal", "Jam"])["Pemain"].apply(list).reset_index()
        
        # 2. Urutkan berdasarkan waktu (terbaru diatas)
        df_match = df_match.sort_values(by=["Tanggal", "Jam"], ascending=False)
        
        # 3. Format Tampilan
        for index, row in df_match.iterrows():
            tgl = row['Tanggal']
            pemain = row['Pemain']
            
            # Pastikan datanya lengkap 4 orang
            if len(pemain) == 4:
                tim_a = f"{pemain[0]} & {pemain[1]}"
                tim_b = f"{pemain[2]} & {pemain[3]}"
                
                with st.expander(f"🏸 Match: {tim_a} vs {tim_b} ({tgl})"):
                    st.markdown(f"""
                    **Tim A:** {pemain[0]}, {pemain[1]}  
                    **Tim B:** {pemain[2]}, {pemain[3]}  
                    *Kock terpakai: 1*
                    """)
            else:
                st.warning(f"Data tidak lengkap pada {tgl}: {', '.join(pemain)}")

else:
    st.info("Belum ada data pemakaian. Yuk main!")

# ==========================================
# 3. FORM INPUT PEMAIN (DIPINDAHKAN KE BAWAH)
# ==========================================
list_pemain = ["Fikri", "Nopek", "Diki", "Sigit", "Mang Oco", "Agus", "Fatah", "Kholid", "Riski"]
list_pemain = sorted(list_pemain) # Optional: Urutkan abjad

with st.container():
    st.write("---")
    st.caption("Catat Game Baru")
    
    with st.form("form_kock"):
        col_depan, col_belakang = st.columns(2)
        with col_depan:
            st.caption("Tim A (Kiri/Depan)")
            p1 = st.selectbox("Pemain 1", list_pemain, index=0)
            p2 = st.selectbox("Pemain 2", list_pemain, index=1)
        with col_belakang:
            st.caption("Tim B (Kanan/Belakang)")
            p3 = st.selectbox("Pemain 3", list_pemain, index=2)
            p4 = st.selectbox("Pemain 4", list_pemain, index=3)

        submitted = st.form_submit_button("🏸 Submit (+1 Kock)")

        if submitted:
            # Update Log
            now = datetime.now()
            tgl = now.strftime("%Y-%m-%d")
            jam = now.strftime("%H:%M:%S")
            pemain_aktif = [p1, p2, p3, p4]
            data_baru_list = []
            for p in pemain_aktif:
                data_baru_list.append({
                    "Tanggal": tgl, "Jam": jam, "Pemain": p, "Jumlah": 1, "Keterangan": "Game Rutin"
                })
            
            df_baru = pd.DataFrame(data_baru_list)
            updated_df = pd.concat([existing_data, df_baru], ignore_index=True)
            conn.update(worksheet="Log_Transaksi", data=updated_df)
            
            # Update Stok (-1)
            sisa_baru = sisa_kock - 1
            df_status.at[0, "Sisa"] = sisa_baru
            conn.update(worksheet="Status_Kock", data=df_status)
            
            st.success(f"Game dicatat! Sisa kock sekarang: {sisa_baru}")
            st.rerun()

# --- TOMBOL UNDO ---
col_undo, col_dummy = st.columns([1, 2])
with col_undo:
    if st.button("↩️ Batalkan Input Terakhir"):
        if len(existing_data) >= 4:
            # Hapus Log Terakhir
            df_koreksi = existing_data.iloc[:-4]
            conn.update(worksheet="Log_Transaksi", data=df_koreksi)
            
            # Balikin Stok (+1)
            sisa_balik = sisa_kock + 1
            df_status.at[0, "Sisa"] = sisa_balik
            conn.update(worksheet="Status_Kock", data=df_status)
            
            st.toast("Input dibatalkan. Kock dikembalikan ke stok.")
            st.rerun()
        else:
            st.warning("Data kosong.")

# --- ADMIN AREA (GABUNGAN) ---
st.write("---")
with st.expander("👮 Admin Area (Stok & Reset)"):
    
    # BAGIAN 1: GANTI TABUNG BARU
    st.subheader("1. Buka Tabung Baru")
    with st.form("form_ganti_stok"):
        merk_baru = st.text_input("Merk Kock Baru", value=nama_kock_aktif)
        stok_baru = st.number_input("Isi Full (biasanya 12)", min_value=1, value=12)
        
        if st.form_submit_button("Buka Tabung Baru"):
            df_status.at[0, "Nama_Kock"] = merk_baru
            df_status.at[0, "Sisa"] = stok_baru
            df_status.at[0, "Total_Isi"] = stok_baru
            conn.update(worksheet="Status_Kock", data=df_status)
            st.success(f"Tabung {merk_baru} dibuka! Stok reset jadi {stok_baru}.")
            st.rerun()

    st.divider()

    # BAGIAN 2: RESET MUSIM (DENGAN PASSWORD)
    st.subheader("2. Reset Musim (Hapus Semua Data)")
    st.caption("Awas! Ini akan menghapus seluruh histori permainan.")
    
    password = st.text_input("Password Admin", type="password")
    
    if st.button("🔥 Hapus Semua Data"):
        if password == "rahasia123": # Ganti password di sini
            # Kosongkan Log Transaksi
            df_kosong = pd.DataFrame(columns=["Tanggal", "Jam", "Pemain", "Jumlah", "Keterangan"])
            conn.update(worksheet="Log_Transaksi", data=df_kosong)
            
            st.success("Data log permainan berhasil di-reset! Siap untuk musim baru.")
            st.rerun()
        else:
            st.error("Password salah!")

