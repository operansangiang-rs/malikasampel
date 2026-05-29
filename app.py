import streamlit as st
import pandas as pd
import json
import os

# Konfigurasi Halaman
st.set_page_config(page_title="Ops Trafo - Malika", layout="wide")

st.title("📦 Sistem Operasional Trafo")

# Inisialisasi Session State (agar data tidak hilang saat input)
if 'df_job' not in st.session_state:
    st.session_state.df_job = pd.DataFrame(columns=["Deskripsi Pekerjaan"])
if 'df_material' not in st.session_state:
    st.session_state.df_material = pd.DataFrame(columns=["Nama Material", "Qty", "Satuan"])

# Membuat Tab Navigasi
tab1, tab2 = st.tabs(["➕ Input Data Baru", "🔍 Cari & Lihat Data"])

# --- TAB 1: INPUT DATA ---
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
            # Mengubah tabel ke JSON agar bisa disimpan di CSV
            new_entry = {
                "Nama Proyek": nama_proyek,
                "Teknisi": teknisi,
                "Tanggal": str(tanggal_kerja),
                "Job": json.dumps(st.session_state.df_job.to_dict()),
                "Material": json.dumps(st.session_state.df_material.to_dict())
            }
            df_new = pd.DataFrame([new_entry])
            
            # Save ke file CSV di root folder
            file_path = "proyek_data.csv"
            df_new.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
            
            st.success("Data berhasil disimpan ke sistem!")
            st.balloons()

# --- TAB 2: LIHAT DATA ---
with tab2:
    st.header("Daftar Proyek")
    
    if os.path.exists("proyek_data.csv"):
        df_all = pd.read_csv("proyek_data.csv")
        
        # Filter Pencarian (Disembunyikan dalam expander agar rapi)
        with st.expander("🔍 Filter Pencarian"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                search_nama = st.text_input("Cari berdasarkan Nama Proyek:")
            with col_s2:
                use_date = st.checkbox("Gunakan filter tanggal")
                search_date = None
                if use_date:
                    search_date = st.date_input("Pilih Tanggal:")

        # Logika Filter Data
        filtered_df = df_all.copy()
        
        if search_nama:
            filtered_df = filtered_df[filtered_df["Nama Proyek"].str.contains(search_nama, case=False)]
        
        if use_date and search_date:
            filtered_df = filtered_df[filtered_df["Tanggal"] == str(search_date)]

        # Menampilkan hasil filter dalam bentuk Accordion (Expander)
        if filtered_df.empty:
            st.warning("Data tidak ditemukan.")
        else:
            for _, row in filtered_df.iterrows():
                with st.expander(f"📌 {row['Nama Proyek']} | 📅 {row['Tanggal']}"):
                    st.write(f"**Teknisi:** {row['Teknisi']}")
                    
                    st.write("**Jobdesk:**")
                    st.dataframe(pd.DataFrame(json.loads(row['Job'])), use_container_width=True)
                    
                    st.write("**Material:**")
                    st.dataframe(pd.DataFrame(json.loads(row['Material'])), use_container_width=True)
    else:
        st.info("Belum ada data yang tersimpan.")
