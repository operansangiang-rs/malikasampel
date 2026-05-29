import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from fpdf import FPDF

# Konfigurasi Halaman
st.set_page_config(page_title="Ops Trafo - Malika", layout="wide")

# --- SISTEM LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
    st.title("🔐 Login Sistem Operasional")
    role_choice = st.selectbox("Pilih Akses Masuk:", ["Pilih...", "Admin", "User"])
    
    if role_choice != "Pilih...":
        password = st.text_input(f"Masukkan Password untuk {role_choice}:", type="password")
        if st.button("Login"):
            if role_choice == "Admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.rerun()
            elif role_choice == "User" and password == "2222":
                st.session_state.logged_in = True
                st.session_state.role = "user"
                st.rerun()
            else:
                st.error("Password Salah!")
    st.stop()

# --- SIDEBAR & STATUS ---
st.sidebar.title("👤 Profil Akun")
st.sidebar.write(f"Status Anda: **{st.session_state.role.upper()}**")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- FUNGSI PDF ---
def generate_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Laporan Proyek: {row['Nama Proyek']}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Tanggal: {row['Tanggal']}", ln=True)
    pdf.cell(200, 10, txt=f"Teknisi: {row['Teknisi']}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Rincian Jobdesk:", ln=True)
    pdf.set_font("Arial", size=10)
    job_df = pd.DataFrame(json.loads(row['Job']))
    pdf.multi_cell(0, 10, txt=job_df.to_string(index=False))
    return pdf.output(dest='S').encode('latin-1')

# --- TAMPILAN UTAMA ---
st.title("📦 Sistem Operasional Trafo")
st.write(f"Selamat datang, Anda login sebagai **{st.session_state.role.upper()}**")

# Inisialisasi Data
if 'df_job' not in st.session_state: st.session_state.df_job = pd.DataFrame(columns=["Deskripsi Pekerjaan"])
if 'df_material' not in st.session_state: st.session_state.df_material = pd.DataFrame(columns=["Nama Material", "Qty", "Satuan"])

# Navigasi Tab
tabs = ["🔍 Cari & Lihat Data", "🔔 Notifikasi"]
if st.session_state.role == "admin":
    tabs.insert(0, "➕ Input Data Baru")
tab_list = st.tabs(tabs)

# --- TAB INPUT (ADMIN ONLY) ---
if st.session_state.role == "admin":
    with tab_list[0]:
        st.header("Tambah Data Proyek")
        col1, col2 = st.columns(2)
        nama_proyek = col1.text_input("Nama Proyek/Lokasi")
        teknisi = col2.text_input("Nama Teknisi")
        tanggal_kerja = st.date_input("Tanggal Pelaksanaan")
        st.subheader("📋 Rincian Pekerjaan")
        st.session_state.df_job = st.data_editor(st.session_state.df_job, num_rows="dynamic", use_container_width=True)
        st.subheader("🛠️ Kebutuhan Material")
        st.session_state.df_material = st.data_editor(st.session_state.df_material, num_rows="dynamic", use_container_width=True)
        if st.button("Simpan Data Proyek"):
            new_entry = {"Nama Proyek": nama_proyek, "Teknisi": teknisi, "Tanggal": str(tanggal_kerja), 
                         "Job": json.dumps(st.session_state.df_job.to_dict()), 
                         "Material": json.dumps(st.session_state.df_material.to_dict())}
            pd.DataFrame([new_entry]).to_csv("proyek_data.csv", mode='a', header=not os.path.exists("proyek_data.csv"), index=False)
            st.success("Data berhasil disimpan!")

# --- TAB CARI & LIHAT DATA ---
idx_lihat = 1 if st.session_state.role == "admin" else 0
with tab_list[idx_lihat]:
    st.header("Daftar Proyek")
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv")
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        
        with st.expander("🔍 Filter Pencarian"):
            c1, c2 = st.columns(2)
            search_nama = c1.text_input("Cari berdasarkan Nama Proyek:")
            use_date = c2.checkbox("Gunakan filter tanggal")
            search_date = c2.date_input("Pilih Tanggal:") if use_date else None
        
        filtered_df = df.copy()
        if search_nama: filtered_df = filtered_df[filtered_df["Nama Proyek"].str.contains(search_nama, case=False)]
        if use_date: filtered_df = filtered_df[filtered_df["Tanggal"].dt.date == search_date]
        
        for idx, row in filtered_df.sort_values(by="Tanggal", ascending=False).iterrows():
            with st.expander(f"📌 {row['Nama Proyek']} | 📅 {str(row['Tanggal'].date())}"):
                st.write(f"**Teknisi:** {row['Teknisi']}")
                st.dataframe(pd.DataFrame(json.loads(row['Job'])), use_container_width=True)
                st.dataframe(pd.DataFrame(json.loads(row['Material'])), use_container_width=True)
                
                # Baris Tombol Aksi
                c_a1, c_a2 = st.columns([1, 5])
                with c_a1:
                    st.download_button("📄 PDF", generate_pdf(row), f"{row['Nama Proyek']}.pdf", "application/pdf")
                
                if st.session_state.role == "admin":
                    with c_a2:
                        if st.button("🗑️ Hapus Proyek", key=f"del_{idx}"):
                            df_new = df.drop(idx)
                            df_new.to_csv("proyek_data.csv", index=False)
                            st.rerun()
    else: st.info("Belum ada data.")

# --- TAB NOTIFIKASI ---
idx_notif = 2 if st.session_state.role == "admin" else 1
with tab_list[idx_notif]:
    st.header("🔔 Proyek Mendatang (7 Hari)")
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv")
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        upcoming = df[(df['Tanggal'] >= pd.Timestamp(datetime.now().date())) & (df['Tanggal'] <= pd.Timestamp(datetime.now().date()) + timedelta(days=7))]
        for _, row in upcoming.iterrows():
            st.info(f"📅 {row['Tanggal'].date()}: {row['Nama Proyek']} (Teknisi: {row['Teknisi']})")
