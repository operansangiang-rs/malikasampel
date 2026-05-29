import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

# Konfigurasi Halaman
st.set_page_config(page_title="Ops Trafo - Malika", layout="wide")

st.title("📦 Sistem Operasional Trafo")

# Inisialisasi Session State
if 'df_job' not in st.session_state:
    st.session_state.df_job = pd.DataFrame(columns=["Deskripsi Pekerjaan"])
if 'df_material' not in st.session_state:
    st.session_state.df_material = pd.DataFrame(columns=["Nama Material", "Qty", "Satuan"])

# Membuat Tab Navigasi
tab1, tab2, tab3 = st.tabs(["➕ Input Data Baru", "🔍 Cari & Lihat Data", "🔔 Notifikasi Proyek"])

# --- TAB 1: INPUT DATA ---
# (Kode Input tetap sama seperti sebelumnya)
with tab1:
    st.header("Tambah Data Proyek")
    col1, col2 = st.columns(2)
    with col1:
        nama_proyek = st.text_input("Nama Proyek/Lokasi")
    with col2:
        teknisi = st.text_input("Nama Teknisi")
    tanggal_kerja = st.date_input("Tanggal Pelaksanaan")
    
    st.subheader("📋 Rincian Pekerjaan")
    st.session_state.df_job = st.data_editor(st.session_state.df_job, num_rows="dynamic", use_container_width=True)
    st.subheader("🛠️ Kebutuhan Material")
    st.session_state.df_material = st.data_editor(st.session_state.df_material, num_rows="dynamic", use_container_width=True)

    if st.button("Simpan Data Proyek"):
        if not nama_proyek:
            st.error("Nama Proyek wajib diisi!")
        else:
            new_entry = {
                "Nama Proyek": nama_proyek,
                "Teknisi": teknisi,
                "Tanggal": str(tanggal_kerja),
                "Job": json.dumps(st.session_state.df_job.to_dict()),
                "Material": json.dumps(st.session_state.df_material.to_dict())
            }
            df_new = pd.DataFrame([new_entry])
            df_new.to_csv("proyek_data.csv", mode='a', header=not os.path.exists("proyek_data.csv"), index=False)
            st.success("Data berhasil disimpan!")

# --- TAB 2: LIHAT DATA ---
with tab2:
    st.header("Daftar Proyek")
    if os.path.exists("proyek_data.csv"):
        df_all = pd.read_csv("proyek_data.csv")
        df_all['Tanggal'] = pd.to_datetime(df_all['Tanggal'])
        df_all = df_all.sort_values(by="Tanggal", ascending=False)
        
        # Filter Pencarian
        with st.expander("🔍 Filter Pencarian"):
            search_nama = st.text_input("Cari berdasarkan Nama Proyek:")
            if search_nama:
                df_all = df_all[df_all["Nama Proyek"].str.contains(search_nama, case=False)]

        for _, row in df_all.iterrows():
            with st.expander(f"📌 {row['Nama Proyek']} | 📅 {str(row['Tanggal'].date())}"):
                st.write(f"**Teknisi:** {row['Teknisi']}")
                st.write("**Jobdesk:**")
                st.dataframe(pd.DataFrame(json.loads(row['Job'])))
                st.write("**Material:**")
                st.dataframe(pd.DataFrame(json.loads(row['Material'])))

# --- TAB 3: NOTIFIKASI ---
with tab3:
    st.header("🔔 Proyek Mendatang (7 Hari ke Depan)")
    if os.path.exists("proyek_data.csv"):
        df_all = pd.read_csv("proyek_data.csv")
        df_all['Tanggal'] = pd.to_datetime(df_all['Tanggal'])
        
        hari_ini = datetime.now()
        tujuh_hari_depan = hari_ini + timedelta(days=7)
        
        # Filter data: Tanggal >= hari ini DAN tanggal <= 7 hari ke depan
        upcoming_df = df_all[(df_all['Tanggal'] >= hari_ini) & (df_all['Tanggal'] <= tujuh_hari_depan)]
        
        if not upcoming_df.empty:
            st.warning(f"Ada {len(upcoming_df)} proyek dalam minggu ini!")
            for _, row in upcoming_df.iterrows():
                st.info(f"📅 **{row['Tanggal'].date()}**: {row['Nama Proyek']} (Teknisi: {row['Teknisi']})")
        else:
            st.success("Tidak ada proyek mendesak dalam 7 hari ke depan.")
    else:
        st.info("Belum ada data proyek.")
