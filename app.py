import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Ops Trafo - Malika", layout="wide")

st.title("📦 Sistem Operasional Trafo")

# Inisialisasi data
if 'df_job' not in st.session_state:
    st.session_state.df_job = pd.DataFrame(columns=["Deskripsi Pekerjaan"])
if 'df_material' not in st.session_state:
    st.session_state.df_material = pd.DataFrame(columns=["Nama Material", "Qty", "Satuan"])

# --- TAB 1: INPUT ---
tab1, tab2 = st.tabs(["➕ Input Data Baru", "🔍 Cari & Lihat Data"])

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
            # Data yang akan disimpan
            new_entry = {
                "Nama Proyek": nama_proyek,
                "Teknisi": teknisi,
                "Tanggal": str(tanggal_kerja),
                "Job": json.dumps(st.session_state.df_job.to_dict()),
                "Material": json.dumps(st.session_state.df_material.to_dict())
            }
            df_new = pd.DataFrame([new_entry])
            
            # Save ke file CSV di folder yang sama (GitHub)
            file_path = "proyek_data.csv"
            df_new.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
            
            st.success("Data berhasil disimpan ke cloud GitHub!")

# --- TAB 2: LIHAT DATA ---
with tab2:
    st.header("Daftar Proyek")
    if os.path.exists("proyek_data.csv"):
        df_all = pd.read_csv("proyek_data.csv")
        search = st.text_input("Cari Nama Proyek:")
        
        if search:
            df_all = df_all[df_all["Nama Proyek"].str.contains(search, case=False)]

        for _, row in df_all.iterrows():
            with st.expander(f"📌 {row['Nama Proyek']} | 📅 {row['Tanggal']}"):
                st.write(f"**Teknisi:** {row['Teknisi']}")
                st.write("**Jobdesk:**")
                st.dataframe(pd.DataFrame(json.loads(row['Job'])))
                st.write("**Material:**")
                st.dataframe(pd.DataFrame(json.loads(row['Material'])))
    else:
        st.info("Belum ada data.")
