import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ops Trafo", layout="wide")

st.title("Sistem Operasional Proyek Trafo")

# Sidebar untuk navigasi
menu = st.sidebar.selectbox("Menu", ["Input Data", "Lihat Proyek"])

if menu == "Input Data":
    st.header("Tambah Data Proyek")
    
    # Form 1: Jobdesk
    with st.form("form_jobdesk"):
        nama_proyek = st.text_input("Nama Proyek")
        nama_teknisi = st.text_input("Nama Teknisi")
        tanggal = st.date_input("Tanggal Kerja")
        deskripsi_kerja = st.text_area("Detail Pekerjaan (Contoh: Kupas Kabel)")
        submit_job = st.form_submit_button("Simpan Jobdesk")
    
    # Form 2: Material (Terpisah)
    st.subheader("Input Material")
    with st.form("form_material"):
        nama_material = st.text_input("Nama Material (Contoh: Tang, Kabel, dll)")
        jumlah = st.number_input("Jumlah", min_value=1)
        submit_material = st.form_submit_button("Tambah Material")

    if submit_job:
        st.success(f"Jobdesk untuk {nama_proyek} telah dicatat!")
        
    if submit_material:
        st.info(f"Material {nama_material} ditambahkan ke daftar.")

elif menu == "Lihat Proyek":
    st.header("Daftar Pekerjaan")
    # Tempat menampilkan tabel data nantinya
    st.write("Belum ada data.")
